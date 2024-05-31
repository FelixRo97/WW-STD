from django.db import models

# Create your models here.

class Lobby(models.Model):    
    lobbyID = models.IntegerField(primary_key=True) 
    observations = models.TextField(default='[]')
    lobbyList = models.TextField(default='{}')
    wwRoles = models.TextField(default='{}')
    roleDistribution = models.TextField(default='{}')
    dBAccessBlocked = models.IntegerField(default=0)
    status = models.TextField(default='lobby') # lobby, standby or game
