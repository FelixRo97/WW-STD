from django.shortcuts import render
from django.http import HttpResponseBadRequest, JsonResponse
import ast
from .models import Lobby
import json

def index(request):
    return render(request, 'index.html')

def lobby(request):

    # TODO how to make refreshing playerNames POST
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
        
    # if there were no cookies, player cannot be important for current lobby
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

def addConfig(request):
    
    roles = ''

    try:                
        
        roles = request.POST.get('roles', '0')
        
    # if there were no cookies, player cannot be important for current lobby
    except KeyError:
        return HttpResponseBadRequest
    
    print(roles)

    alterDB()
    return JsonResponse(status=200)

def gameWW(request):
    # TODO block lobby & game session for new player from now on

    playerID = ''
    playerName = ''

    try:                
        playerID = str(ast.literal_eval(request.COOKIES['userData']).get('playerID'))
        playerName = str(ast.literal_eval(request.COOKIES['userData']).get('playerName'))
        
    # if there were no cookies, player cannot be important for current lobby
    except KeyError:
        return render(request, 'index.html')
    
    return render(request, 'game.html')

def gameSH(request):
    # TODO block lobby & game session for new player from now on

    playerID = ''
    playerName = ''

    try:                
        playerID = str(ast.literal_eval(request.COOKIES['userData']).get('playerID'))
        playerName = str(ast.literal_eval(request.COOKIES['userData']).get('playerName'))
        
    # if there were no cookies, player cannot be important for current lobby
    except KeyError:
        return render(request, 'index.html')
    
    return render(request, 'game.html')
        
def alterDB(idLobby=0, countLobby=None, removeFromLobby=None, addToLobby=None, matching=None, stat=None):

    dbAltered = False
    ref = ''

    while not dbAltered:

        lobbies = Lobby.objects.filter(lobbyID=idLobby)
        ref = lobby

        for lobby in lobbies:
            
            # wait for exclusive access
            if lobby.accessBlocked == 1:
                break

            # add player in DB
            lobby.accessBlocked = 1
            lobby.save()

            if (removeFromLobby != None):
                lobbyList = ast.literal_eval(lobby.lobbyList)
                if removeFromLobby in lobbyList:
                    del lobbyList[removeFromLobby]

                lobby.lobbyList = str(lobbyList)

            elif (addToLobby != None):
                
                playerID = addToLobby[0]
                playerName = addToLobby[1]
                lobbyList = ast.literal_eval(lobby.lobbyList)

                # check if DB update is necessary
                playerInDB =playerID in lobbyList and lobbyList[playerID] == playerName # addToLobby = [playerID, playerName]
                if playerInDB:                
                    dbAltered = True
                    break       

                lobbyList[playerID] = playerName            
                lobby.lobbyList = str(lobbyList) 
                
            elif (matching != None):
                lobby.roleMatching = matching

            elif (stat != None):
                lobby.status = stat

            elif (countLobby != None):
                pass

            lobby.accessBlocked = 0
            lobby.save()
            
            dbAltered = True
            break
    
    return ref

     