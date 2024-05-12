from django.shortcuts import render
from django.http import HttpResponseBadRequest, JsonResponse
import ast
from .models import Lobby
import random

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
    
    # TODO error catching
    lobbyList = ast.literal_eval(alterDB(idLobby=0, addToLobby=[playerID, playerName]).lobbyList)
    return render(request, 'lobby.html', {'lobbyList': lobbyList})

def werwolfList(request):
    
    # TODO block lobby for new player

    playerCount = blockLobby()
    return render(request, 'werwolfList.html', {'playerCount': playerCount})

def removePlayer(request):
        
    playerID = ''

    try:                
        playerID = str(ast.literal_eval(request.COOKIES['userData']).get('playerID'))
        
    # if there were no cookies, player cannot be important for current lobby
    except KeyError:
        return render(request, 'index.html')

    alterDB(idLobby=0, removeFromLobby=playerID)
        
    return render(request, 'index.html')

# add specified Werwolf roles
def addRoles(request):
    
    roles = ''

    try:                
        
        roles = ast.literal_eval(request.POST.get('roles', '0'))
        
    # if there were no cookies, player cannot be important for current lobby
    except KeyError:
        return HttpResponseBadRequest
    
    template = {}

    for role in roles:
        template[role] = ""

    alterDB(matching=str(template))
    return JsonResponse({}, status=200)

# Werwolf game session
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

# Sec Hit game session
def gameSH(request):
    
    playerCount = blockLobby()
    if playerCount == 0:
        print("Error 0")
        return HttpResponseBadRequest # TODO replace with invalidGameState.html oder so
    
    lobbyID = 0

    #try:                
    #    id = str(ast.literal_eval(request.COOKIES['userData']).get(???)))
    
        
    # if there were no cookies, player cannot be important for current lobby
    #except KeyError:
    #    return render(request, 'index.html')

    # TODO move below to role distribution and return current matching in distribution if game already started and / or its not the 
    # player one who made the call

    roles = {"Hitler": 1, "Faschist": 0, "Liberal": 0}

    if (playerCount < 5):
        print("Error 1")
        return HttpResponseBadRequest # TODO replace with invalidGameState.html oder so

    elif (playerCount < 7):

        roles["Faschist"] = 1
        roles["Liberal"] = playerCount-2
        
    elif (playerCount < 9):
        
        roles["Faschist"] = 2
        roles["Liberal"] = playerCount-3

    elif (playerCount < 11):

        roles["Faschist"] = 3
        roles["Liberal"] = playerCount-4
    
    else:
        print("Error 2")
        return HttpResponseBadRequest # TODO replace with invalidGameState.html oder so
    
    distribution = roleDistributionSH(roles, lobbyID)
    if not distribution:
        print("Error 3")
        return HttpResponseBadRequest # TODO replace with invalidGameState.html oder so
    
    if (alterDB(matching=distribution) == ''):
        print("Error 4")
        return HttpResponseBadRequest # TODO replace with invalidGameState.html oder so
        
    print(distribution)
         
    return render(request, 'game.html')
        
# alter DB with ONE of the possible parameters
def alterDB(idLobby=0, countLobby=None, removeFromLobby=None, addToLobby=None, matching=None, stat=None):
    # TODO check if lobby is closed, if yes return ''
    dbAltered = False
    ref = ''

    while not dbAltered:

        lobbies = Lobby.objects.filter(lobbyID=idLobby)
        
        for lobby in lobbies:
            
            ref = lobby

            if (addToLobby != None):
                
                playerID = addToLobby[0]
                playerName = addToLobby[1]
                lobbyList = ast.literal_eval(lobby.lobbyList)

                # check if DB update is necessary
                playerInDB =playerID in lobbyList and lobbyList[playerID] == playerName # addToLobby = [playerID, playerName]
                if playerInDB:                
                   dbAltered = True
                   break

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

                lobbyList[playerID] = playerName            
                lobby.lobbyList = str(lobbyList)     
                
            elif (matching != None):
                lobby.roleMatching = matching

            elif (stat != None):
                lobby.status = stat

            elif (countLobby != None):
                pass

            else:
                print("##### Info: Nothing changed although called intentionally!")
            
            lobby.accessBlocked = 0
            lobby.save()
            
            dbAltered = True
            break
    
    return ref

# set game mode to game -> no new players can enter and count player
def blockLobby(lobbyID=0):

    lobbyList = ast.literal_eval(alterDB(idLobby=lobbyID, stat="game").lobbyList)
    if lobbyList != '':
        return len(lobbyList)
    return 0 
   
def roleDistributionSH(roleTemplate:dict, idLobby:int = 0):

    try: 
        lobbies = Lobby.objects.filter(lobbyID=idLobby)
        players = {}

        for lobby in lobbies:
            
            players = ast.literal_eval(lobby.lobbyList)
            break

        distribution = {}

        for role in roleTemplate:

            while roleTemplate[role] != 0:

                currentPlayer = random.choice(list(players.items()))
                distribution[currentPlayer] = role

                del players[currentPlayer[0]]
                roleTemplate[role] -= 1

    except Exception as e:
        print(e)
        return False

    return distribution

def roleDistributionWW():
    pass

