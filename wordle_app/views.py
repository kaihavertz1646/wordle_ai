from django.shortcuts import render, redirect
from django.http import JsonResponse
import random
import csv
import os
from collections import Counter
import math

CSV_PATH = os.path.join(os.path.dirname(__file__), 'data', 'words.csv')

# Load the words here
def load_words(csv_path):
    with open(csv_path, 'r') as file:
        reader = csv.reader(file)
        words_list = [row[0] for row in reader]
    return words_list

words = load_words(CSV_PATH)

from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
import random

def index(request):
    if request.method == 'POST':
        login_form = AuthenticationForm(data=request.POST)
        signup_form = UserCreationForm(request.POST)
        if 'login' in request.POST:
            if login_form.is_valid():
                user = login_form.get_user()
                login(request, user)
                return redirect('play')
        elif 'signup' in request.POST:
            if signup_form.is_valid():
                user = signup_form.save()
                username = signup_form.cleaned_data.get('username')
                raw_password = signup_form.cleaned_data.get('password1')
                user = authenticate(username=username, password=raw_password)
                login(request, user)
                return redirect('play')
    else:
        login_form = AuthenticationForm()
        signup_form = UserCreationForm()

    # Initialize game state in session
    request.session['solution'] = random.choice(words)
    request.session['ai_possible_words'] = words.copy()
    request.session['ai_guesses'] = []
    request.session['user_guesses'] = []
    request.session['user_feedbacks'] = []

    return render(request, 'wordle_app/index.html', {'form': login_form, 'signup_form': signup_form})

import json
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt  # Only for testing; consider CSRF protection later
def play(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            guess = data.get('guess')
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        if guess is None:
            return JsonResponse({'error': 'No guess provided'}, status=400)

        solution = request.session['solution']
        ai_possible_words = request.session['ai_possible_words']
        ai_guesses = request.session['ai_guesses']
        user_guesses = request.session.get('user_guesses', [])
        user_feedbacks = request.session.get('user_feedbacks', [])

        user_feedback = check_guess(guess, solution)
        user_won = guess == solution

        user_guesses.append(guess)
        user_feedbacks.append(user_feedback)

        if user_won:
            ai_feedback = ['correct'] * len(solution)
            ai_won = True
            ai_guess_word = solution
            game_result(request, 'win')
        else:
            ai_guess_word = ai_guess(ai_possible_words, ai_guesses, user_guesses, user_feedbacks)
            ai_feedback = check_guess(ai_guess_word, solution)
            ai_won = ai_guess_word == solution
            if ai_won:
                game_result(request, 'lose')
        
        ai_guesses.append((ai_guess_word, ai_feedback))
        ai_possible_words = filter_words(ai_possible_words, ai_guesses)

        request.session['ai_possible_words'] = ai_possible_words
        request.session['ai_guesses'] = ai_guesses
        request.session['user_guesses'] = user_guesses
        request.session['user_feedbacks'] = user_feedbacks

        return JsonResponse({
            'user_guess': guess,
            'user_feedback': user_feedback,
            'ai_guess': ai_guess_word,
            'ai_feedback': ai_feedback,
            'user_won': user_won,
            'ai_won': ai_won,
        })
    
    return render(request, 'wordle_app/game.html')



def reset(request):
    # Reinitialize game state
    request.session['solution'] = random.choice(words)
    request.session['ai_possible_words'] = words.copy()
    request.session['ai_guesses'] = []
    request.session['user_guesses'] = []
    request.session['user_feedbacks'] = []
    return redirect('index')

def check_guess(guess, solution):
    feedback = ['absent'] * len(guess)
    solution_frequency = {}

    for letter in solution:
        if letter in solution_frequency:
            solution_frequency[letter] += 1
        else:
            solution_frequency[letter] = 1

    for i in range(len(guess)):
        if guess[i] == solution[i]:
            feedback[i] = 'correct'
            solution_frequency[guess[i]] -= 1

    for i in range(len(guess)):
        if feedback[i] == 'correct':
            continue
        if guess[i] in solution_frequency and solution_frequency[guess[i]] > 0:
            feedback[i] = 'present'
            solution_frequency[guess[i]] -= 1

    return feedback

def entropy(possible_words):
    letter_position_counts = [Counter() for _ in range(5)]
    total_words = len(possible_words)

    for word in possible_words:
        for i, letter in enumerate(word):
            letter_position_counts[i][letter] += 1

    entropy_value = 0
    for i in range(5):
        for count in letter_position_counts[i].values():
            probability = count / total_words
            entropy_value -= probability * math.log2(probability)

    return entropy_value

def ai_guess(possible_words, ai_guesses, user_guesses, user_feedbacks):
    combined_guesses = ai_guesses + list(zip(user_guesses, user_feedbacks))
    filtered_words = filter_words(possible_words, combined_guesses)

    if not filtered_words:
        filtered_words = possible_words

    # If few guesses made, use frequency analysis
    if len(ai_guesses) + len(user_guesses) < 3:
        return frequency_based_guess(filtered_words)
    else:
        return entropy_based_guess(filtered_words)

def frequency_based_guess(filtered_words):
    positional_frequency = [Counter() for _ in range(5)]
    for word in filtered_words:
        for i, letter in enumerate(word):
            positional_frequency[i][letter] += 1

    word_scores = {word: sum(positional_frequency[i][letter] for i, letter in enumerate(word)) for word in filtered_words}
    return max(word_scores, key=word_scores.get)

def entropy_based_guess(filtered_words):
    best_entropy = -1
    best_word = None

    for word in filtered_words:
        new_possible_words = filter_words(filtered_words, [(word, ['correct'] * 5)])
        word_entropy = entropy(new_possible_words)

        if word_entropy > best_entropy:
            best_entropy = word_entropy
            best_word = word

    return best_word


def filter_words(possible_words, combined_guesses):
    if not possible_words:
        return []

    filtered_words = possible_words.copy()

    for guess, feedback in combined_guesses:
        filtered_words = [
            word for word in filtered_words if matches_feedback(word, guess, feedback)
        ]

    return filtered_words if filtered_words else possible_words

def matches_feedback(word, guess, feedback):
    if len(word) != len(guess):
        return False

    word_letter_count = Counter(word)
    guess_letter_count = Counter(guess)

    for i in range(len(guess)):
        if feedback[i] == 'correct':
            if word[i] != guess[i]:
                return False
            word_letter_count[guess[i]] -= 1
            if word_letter_count[guess[i]] < 0:
                return False
        elif feedback[i] == 'present':
            if word[i] == guess[i] or guess[i] not in word:
                return False
            word_letter_count[guess[i]] -= 1
            if word_letter_count[guess[i]] < 0:
                return False

    for i in range(len(guess)):
        if feedback[i] == 'absent' and guess[i] in word:
            if word_letter_count[guess[i]] > 0:
                return False

    return True

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import UserStats


@login_required
def get_user_stats(request):
    user = request.user
    stats, created = UserStats.objects.get_or_create(user=user, defaults={'games_played': 0, 'games_won': 0})
    return JsonResponse({
        'games_played': stats.games_played,
        'games_won': stats.games_won,
    })

from django.shortcuts import get_object_or_404
from .models import UserStats

def game_result(request, result):
    user_stats, created = UserStats.objects.get_or_create(user=request.user, defaults={'games_played': 0, 'games_won': 0})
    
    user_stats.games_played += 1
    if result == 'win':
        user_stats.games_won += 1
    user_stats.save()

    
def stats_view(request):
    user_stats = get_object_or_404(UserStats, user=request.user)
    return render(request, 'game.html', {'user_stats': user_stats})

