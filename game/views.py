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
        playerName = str(ast.literal_eval(request.COOKIES['userData']).get('playerName'))
        playerID = str(ast.literal_eval(request.COOKIES['userData']).get('playerID'))
        
    except KeyError:
        return HttpResponseBadRequest
    
    dbAltered = False
    while not dbAltered:

        lobbies = Lobby.objects.filter(lobbyID=0)

        for lobby in lobbies:

            # check if DB update is necessary
            lobbyList = ast.literal_eval(lobby.lobbyList)
            playerInDB = playerID in lobbyList and lobbyList[playerID] == playerName
            if playerInDB:
                print('already')
                dbAltered = True
                break

            # wait for exclusive access
            if lobby.accessBlocked == 1:
                break

            # add player in DB
            lobby.accessBlocked = 1
            lobby.save()
                           
            lobbyList[playerID] = playerName
            print('####lobbyList')
            print(lobbyList)
            lobby.lobbyList = str(lobbyList)
            print(lobby.lobbyList)
            lobby.accessBlocked = 0
            lobby.save()
            
            dbAltered = True
            break

        return render(request, 'lobby.html', {'lobbyList': lobbyList})

     
    

