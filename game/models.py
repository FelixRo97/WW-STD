from django.db import models

# Create your models here.

class Lobby(models.Model):    
    lobbyID = models.IntegerField() 
    lobbyCount = models.IntegerField() 
    lobbyList = models.TextField(null=True)
