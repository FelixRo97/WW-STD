from django.db import models

# Create your models here.

class Lobby(models.Model):    
    lobbyID = models.IntegerField(primary_key=True) 
    lobbyCount = models.IntegerField() 
    lobbyList = models.TextField()
    roleMatching = models.TextField()
    accessBlocked = models.IntegerField()
    # status = models.TextField() # Lobby, RoleSelection, InGame
