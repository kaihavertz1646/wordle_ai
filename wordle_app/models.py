from django.db import models
from django.contrib.auth.models import User

class UserStats(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    games_played = models.IntegerField(default=0)
    games_won = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} Stats"
