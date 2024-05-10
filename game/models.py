from django.db import models

# Create your models here.

class Lobby(models.Model):    
    lobbyID = models.IntegerField(primary_key=True) 
    lobbyCount = models.IntegerField() # useless?
    lobbyList = models.TextField()
    roleMatching = models.TextField()
    accessBlocked = models.IntegerField()
    status = models.TextField() # lobby or game
