from django.db import models

# Create your models here.

class Lobby(models.Model):    
    lobbyID = models.IntegerField(primary_key=True) 
    observations = models.TextField()
    lobbyList = models.TextField()
    roleDistribution = models.TextField()
    dBAccessBlocked = models.IntegerField()
    status = models.TextField() # lobby, standby or game
