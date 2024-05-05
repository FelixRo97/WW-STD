from django.shortcuts import render
from django.http import HttpResponseBadRequest
import ast
from .models import Lobby
import json

def index(request):
    return render(request, 'index.html')

def lobby(request):

    #if request.method != 'POST': 
     #   return HttpResponseBadRequest  
    
    
    playerName = ''
    playerID = ''

    try:
        print(request.COOKIES['userData'])
        playerName = str(ast.literal_eval(request.COOKIES['userData']).get('playerName'))
        playerID = str(ast.literal_eval(request.COOKIES['userData']).get('playerID'))
        
    except KeyError:
        return HttpResponseBadRequest
    #new = Lobby(lobbyID=0, lobbyCount=0, lobbyList="{}")
    #new.save()
    # TODO get exclusive here
    lobbies = Lobby.objects.filter(lobbyID=0)

    for lobby in lobbies:
        lobbyList = ast.literal_eval(lobby.lobbyList)
        lobbyList[playerName] = playerID

        lobby.list = str(lobbyList)
        lobby.save()
        break
    
    ##
    return render(request, 'lobby.html', {'lobbyList': lobbyList})

     
    

