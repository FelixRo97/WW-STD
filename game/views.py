from django.shortcuts import render
from django.http import HttpResponseBadRequest, JsonResponse
import ast
from .models import Lobby

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
    # TODO block lobby & game session for new player from now on

    idLobby = 0
    

    #try:                
    #    id = str(ast.literal_eval(request.COOKIES['userData']).get(???)))
    
        
    # if there were no cookies, player cannot be important for current lobby
    #except KeyError:
    #    return render(request, 'index.html')
    
    playerCount = blockLobby()

    lobbies = Lobby.objects.filter(lobbyID=idLobby)

    
    return render(request, 'game.html')
        
# alter DB with ONE of the possible parameters
def alterDB(idLobby=0, countLobby=None, removeFromLobby=None, addToLobby=None, matching=None, stat=None):

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
    return len(lobbyList)