from django.shortcuts import render
from django.http import HttpResponseBadRequest
import ast
from .models import Lobby
import json

def index(request):
    return render(request, 'index.html')

def lobby(request):

    # TODO how to make POST
    #if request.method != 'POST': 
    #    return HttpResponseBadRequest  
    

    # TODO make player names unique
    # TODO if lobby status is ingame and player is in lobby list -> forward to game session else show that session is closed

    playerName = ''
    playerID = ''

    try:        
        playerName = str(ast.literal_eval(request.COOKIES['userData']).get('playerName'))
        playerID = str(ast.literal_eval(request.COOKIES['userData']).get('playerID'))
        
    # if there were no cookies, player cannot be important for current lobby
    except KeyError:
        return render(request, 'index.html')
    
    dbAltered = False
    while not dbAltered:

        lobbies = Lobby.objects.filter(lobbyID=0)

        for lobby in lobbies:

            # check if DB update is necessary
            lobbyList = ast.literal_eval(lobby.lobbyList)
            playerInDB = playerID in lobbyList and lobbyList[playerID] == playerName
            if playerInDB:                
                dbAltered = True
                break

            # wait for exclusive access
            if lobby.accessBlocked == 1:
                break

            # add player in DB
            lobby.accessBlocked = 1
            lobby.save()
                           
            lobbyList[playerID] = playerName            
            lobby.lobbyList = str(lobbyList)            
            lobby.accessBlocked = 0
            lobby.save()
            
            dbAltered = True
            break

        return render(request, 'lobby.html', {'lobbyList': lobbyList})

def werwolfList(request):
    # TODO also pass current playerCount
    # TODO block lobby for new player
    return render(request, 'werwolfList.html')

def removePlayer(request):
        
    playerID = ''

    try:                
        playerID = str(ast.literal_eval(request.COOKIES['userData']).get('playerID'))
        
    except KeyError:
        return render(request, 'index.html')

    dbAltered = False
    while not dbAltered:

        lobbies = Lobby.objects.filter(lobbyID=0)

        for lobby in lobbies:
        
            lobbyList = ast.literal_eval(lobby.lobbyList)
                
            # wait for exclusive access
            if lobby.accessBlocked == 1:
                break

            # add player in DB
            lobby.accessBlocked = 1
            lobby.save()

            lobbyList = ast.literal_eval(lobby.lobbyList)
            if playerID in lobbyList:
                del lobbyList[playerID]

            lobby.lobbyList = str(lobbyList)
            lobby.accessBlocked = 0
            lobby.save()
            
            dbAltered = True
            break
        
    return render(request, 'index.html')

def game(request):
    # TODO block lobby & game session for new player from now on
    return render(request, 'game.html')
     
    

