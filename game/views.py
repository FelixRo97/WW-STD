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
    lobbyID = 0

    try:        
        playerName = str(ast.literal_eval(request.COOKIES['userData']).get('playerName'))
        playerID = str(ast.literal_eval(request.COOKIES['userData']).get('playerID'))
        
    # if there were no cookies, player cannot be important for current lobby
    except KeyError:
        return render(request, 'index.html')
    
    if playerName == "resetLobby":
        alterDB(idLobby=lobbyID, reset=True)
        return render(request, 'resetSuccess.html')
    
    lobby = Lobby.objects.filter(lobbyID=lobbyID)[0]
    lobbyList = ast.literal_eval(lobby.lobbyList)
    
    for player in lobbyList:
        if playerName == lobbyList[player] and player != playerID:
            # TODO replace with change name HTML
            return HttpResponseBadRequest
            
    lobby = alterDB(idLobby=lobbyID, addToLobby=[playerID, playerName])
    if lobby == '':
        return HttpResponseBadRequest
    
    lobbyList = ast.literal_eval(lobby.lobbyList)
    if playerID in lobbyList:
        return render(request, 'lobby.html', {'lobbyList': lobbyList, 'gameState': lobby.status})
    
    #TODO return gameClosed.html
    return HttpResponseBadRequest

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

    alterDB(distribution=str(template))
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
        reopenLobby()
        print("Error 0")
        return render(request, 'invalidGameState.html')
    
    lobbyID = 0
    playerID = ''
    playerName = ''

    try:                
        playerID = str(ast.literal_eval(request.COOKIES['userData']).get('playerID'))
        playerName = str(ast.literal_eval(request.COOKIES['userData']).get('playerName'))
        
    # if there were no cookies, player cannot be important for current lobby
    except KeyError:
        return render(request, 'index.html')

    distribution = roleDistributionSH(playerCount, playerID, lobbyID)
    if not distribution:
        print("Error 4")
        return render(request, 'index.html')
    
    output = setOutputSH(playerID, playerName, distribution, playerCount, lobbyID=lobbyID)
    
    return render(request, 'gameSH.html', output)
        
# alter DB with ONE of the possible parameters
def alterDB(idLobby:int=0, observation:dict=None, removeFromLobby:str=None, addToLobby:list=None, distribution:dict=None, stat:str=None, reset:bool=False):
    # TODO check if lobby is closed, if yes return ''
    
    dbAltered = False
    res = ''

    while not dbAltered:

        lobby = Lobby.objects.filter(lobbyID=idLobby)[0]
        res = lobby
       
        if addToLobby != None:
            
            playerID = addToLobby[0]
            playerName = addToLobby[1]
            lobbyList = ast.literal_eval(lobby.lobbyList)

            # check if DB update is necessary
            playerInDB =playerID in lobbyList and lobbyList[playerID] == playerName # addToLobby = [playerID, playerName]
            if playerInDB:                
                dbAltered = True
                break

        # wait for exclusive access
        if lobby.dBAccessBlocked == 1:
            continue

        # add player in DB
        lobby.dBAccessBlocked = 1
        lobby.save()
       
        if removeFromLobby != None:

            lobbyList = ast.literal_eval(lobby.lobbyList)
            if removeFromLobby in lobbyList:
                del lobbyList[removeFromLobby]

            lobby.lobbyList = str(lobbyList)

        elif addToLobby != None:
            
            playerID = addToLobby[0]
            playerName = addToLobby[1]
            lobbyList = ast.literal_eval(lobby.lobbyList)

            lobbyList[playerID] = playerName            
            lobby.lobbyList = str(lobbyList)     
            
        elif distribution != None:
            lobby.roleDistribution = distribution

        # only allow to advance in state when its not a reset
        elif stat != None:
            
            if not (stat == "standby" and "game" in lobby.status):
                lobby.status = stat

        elif observation!= None:

            observations = ast.literal_eval(lobby.observations)
            observations.append(observation)
            lobby.observations = observations

        elif reset == True:

            lobby.observations = []
            lobby.lobbyList = {}
            lobby.roleDistribution = {}
            lobby.status = "lobby"

        else:
            print("##### Info: Nothing changed although called intentionally!")
        
        lobby.dBAccessBlocked = 0
        lobby.save()
        
        dbAltered = True
        break
    
    return res

# set game mode to game -> no new players can enter and count player
def blockLobby(lobbyID:int=0):

    lobbyList = ast.literal_eval(alterDB(idLobby=lobbyID, stat="standby").lobbyList)
    if lobbyList != '':
        return len(lobbyList)
    return 0 

# TODO make compatible with different lobbies (read from cookies?)
def reopenLobby(request):
    
    lobbyID = 0    
    lobbyList = ast.literal_eval(alterDB(idLobby=lobbyID, stat="lobby").lobbyList)
    if lobbyList != '':
        return lobby(request)
    return render(request, 'index.html')

def roleDistributionSH(playerCount:int, playerID:str, idLobby:int = 0)-> dict:

    roles = {"Hitler": 1, "Faschist": 0, "Liberal": 0}

    if (playerCount < 5):
        print("Error 1")
        return False

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
        return False

    try:
    
        lobby = Lobby.objects.filter(lobbyID=idLobby)[0]
        gameState = ''
        players = {}
        distribution = {}

        players = ast.literal_eval(lobby.lobbyList)
        distribution = ast.literal_eval(lobby.roleDistribution)
        gameState = lobby.status

        # only player One should be able to start the game
        lobbyHost = list(players.keys())[0]
        
        if (lobbyHost == playerID) and (gameState == 'standby'):

            distribution = {}

            for role in roles:

                while roles[role] != 0:

                    currentPlayer = random.choice(list(players.items()))
                    distribution[currentPlayer] = role

                    del players[currentPlayer[0]]
                    roles[role] -= 1

            if (alterDB(distribution=distribution, stat="gameSH") == ''):
                print("Error 3")
                return False
        else:
            print('#### Skipped!')
        
    except Exception as e:
        print(e)
        return False

    return distribution

def setOutputSH(playerID:str, playerName:str, distribution:dict, playerCount:int, lobbyID:int)-> dict: 
    
    # dist {ID:Name, ...}
    role = distribution[(playerID, playerName)]
    output = {"role": role, "allies": "", "hitler": ""}

    faschists = []

    if role != "Liberal":

        for player in distribution:

            playerRole = distribution[player]

            if playerRole == "Hitler":

                output["hitler"] = player[1]
            
            # only append other players names
            elif playerRole == "Faschist" and player[0] != playerID:
                faschists.append(player[1])

        if playerCount < 7:
            output["allies"] = faschists
            
        elif role != "Hitler":
            output["allies"] = faschists

    output["lobby"] = []
    # only add other players
    for player in distribution:
        if player[1] != playerName:
            output["lobby"].append(player[1])

    lobby = Lobby.objects.filter(lobbyID=lobbyID)[0]
    output["observations"] = ast.literal_eval(lobby.observations)
    
    return output

# TODO alterDB and indicate the request, query that parameter in setOutput
def requestRoleSH(request):
    
    playerName = ''
    playerToWatch = ''
    lobbyID = 0

    try:        
        playerToWatch = request.POST.get('playerToWatch', '0')
        playerName = str(ast.literal_eval(request.COOKIES['userData']).get('playerName'))
        
    # if there were no cookies, player cannot be important for current lobby
    except KeyError:
        return JsonResponse({}, status=504)    
    
    lobby = Lobby.objects.filter(lobbyID=lobbyID)[0]
    curDistribution = ''
    resRole = ''

    curDistribution = ast.literal_eval(lobby.roleDistribution)
    
    for player in curDistribution:
        
        if player[1] == playerToWatch:
           
            resRole = curDistribution[player]

            if resRole == "Hitler":
                resRole = "Faschist"
            break

    alterDB(observation=[playerName, playerToWatch])
    return JsonResponse({playerToWatch: resRole}, status=200)

def roleDistributionWW()-> dict:
    pass

def outputWW()-> dict:
    pass