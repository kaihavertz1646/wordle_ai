document.getElementById('reset-button').addEventListener('click', function() {
    fetch(resetUrl)
    .then(response => {
        if (response.ok) {
            window.location.reload();
        }
    });
});

document.getElementById('guess-form').onsubmit = function(e) {
    e.preventDefault();
    fetch(playUrl, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,  // Use the csrftoken variable here
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            guess: document.querySelector('input[name="guess"]').value
        })
    })
    .then(response => response.json())
    .then(data => {
        updateBoard('user-board', data.user_guess, data.user_feedback);
        updateBoard('ai-board', data.ai_guess, data.ai_feedback);
        updateKeyboard(data.user_guess, data.user_feedback);
        updateKeyboard(data.ai_guess, data.ai_feedback);

        if (data.user_won || data.ai_won) {
            document.getElementById('guess-form').style.display = 'none';
            if (data.user_won) {
                document.getElementById('result').textContent = 'You won!';
            } else if (data.ai_won) {
                document.getElementById('result').textContent = 'AI won!';
            }
        }
    });
};

function updateBoard(boardId, guess, feedback) {
    const board = document.getElementById(boardId);
    const row = document.createElement('div');
    row.classList.add('row');
    for (let i = 0; i < guess.length; i++) {
        const cell = document.createElement('div');
        cell.classList.add('cell');
        cell.textContent = guess[i];
        if (feedback[i] == 'correct') {
            cell.style.backgroundColor = 'green';
        } else if (feedback[i] == 'present') {
            cell.style.backgroundColor = 'yellow';
        } else {
            cell.style.backgroundColor = 'gray';
        }
        row.appendChild(cell);
    }
    board.appendChild(row);
}

function updateKeyboard(guess, feedback) {
    const keys = document.querySelectorAll('.key');
    const keyMap = {};
    keys.forEach(key => {
        keyMap[key.textContent] = key;
    });

    for (let i = 0; i < guess.length; i++) {
        if (feedback[i] == 'correct') {
            keyMap[guess[i].toUpperCase()].style.backgroundColor = 'green';
        } else if (feedback[i] == 'present') {
            if (keyMap[guess[i].toUpperCase()].style.backgroundColor !== 'green') {
                keyMap[guess[i].toUpperCase()].style.backgroundColor = 'yellow';
            }
        } else {
            if (keyMap[guess[i].toUpperCase()].style.backgroundColor !== 'green' && keyMap[guess[i].toUpperCase()].style.backgroundColor !== 'yellow') {
                keyMap[guess[i].toUpperCase()].style.backgroundColor = 'gray';
            }
        }
    }
}

var modal = document.getElementById("statsModal");
var btn = document.getElementById("stats-button");
var span = document.getElementsByClassName("close")[0];

btn.onclick = function() {
    fetch(getUserStatsUrl)
    .then(response => response.json())
    .then(data => {
        document.getElementById('games-played').textContent = data.games_played;
        document.getElementById('games-won').textContent = data.games_won;
        modal.style.display = "block"; // Shows the modal
    });
}


span.onclick = function() {
    modal.style.display = "none";
}

window.onclick = function(event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
}

// Function to get the CSRF token from cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');
