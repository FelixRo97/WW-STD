from django.shortcuts import render
from django.http import JsonResponse
import ast
from .models import Lobby
import random

def index(request):
    return render(request, 'index.html')

def lobby(request):

    # TODO how to make refreshing playerNames POST
    #if request.method != 'POST': 
    #    return HttpResponseBadRequest  
    
    # TODO if lobby status is ingame and player is in lobby list -> forward to game session else show that session is closed

    playerName = ''
    playerID = ''
    lobbyID = 0

    try:        
        playerName = str(ast.literal_eval(request.COOKIES['userData']).get('playerName'))
        playerID = str(ast.literal_eval(request.COOKIES['userData']).get('playerID'))
        
    # if there were no cookies, player cannot be important for current lobby
    except KeyError:
        return render(request, 'invalidGameState.html')
    
    if playerName == "resetLobby":
        
        if alterDB(idLobby=lobbyID, reset=True) != None:
            return render(request, 'resetSuccess.html')
        
        return render(request, 'invalidGameState.html')
    
    lobby = Lobby.objects.filter(lobbyID=lobbyID)[0]
    lobbyList = ast.literal_eval(lobby.lobbyList)
    
    isInLobby = False
    for player in lobbyList:
        if playerName == lobbyList[player]:
            
            if player != playerID:
                return render(request, 'changeName.html')
            else:
                isInLobby = True
    
    # block new player if lobby is in standby+ status
    if not isInLobby and lobby.status != 'lobby':
        return render(request, 'gameClosed.html')
            
    lobby = alterDB(idLobby=lobbyID, addToLobby=[playerID, playerName])
    if lobby == None:
        return render(request, 'invalidGameState.html')
    
    lobbyList = ast.literal_eval(lobby.lobbyList)
    if playerID in lobbyList:
        return render(request, 'lobby.html', {'lobbyList': lobbyList, 'gameState': lobby.status})
    
    return render(request, 'invalidGameState.html')

def removePlayer(request):
        
    playerID = ''
    lobbyID = 0

    try:                
        playerID = str(ast.literal_eval(request.COOKIES['userData']).get('playerID'))
        
    # if there were no cookies, player cannot be important for current lobby
    except KeyError:
        return render(request, 'invalidGameState.html')

    if alterDB(idLobby=lobbyID, removeFromLobby=playerID) == None:
        return render(request, 'invalidGameState.html')
        
    return render(request, 'index.html')

def werwolfList(request):
    
    playerID = ''
    lobbyID = 0

    try:                
        playerID = str(ast.literal_eval(request.COOKIES['userData']).get('playerID'))
        
    # if there were no cookies, player cannot be important for current lobby
    except KeyError:
        return render(request, 'invalidGameState.html')

    playerCount = blockLobby(playerID, lobbyID)
    return render(request, 'werwolfList.html', {'playerCount': playerCount})

# add specified Werwolf roles
def addRoles(request):
    
    lobbyID = 0
    roles = ''

    try:                
        
        roles = ast.literal_eval(request.POST.get('roles', '0'))
        
    # if there were no cookies, player cannot be important for current lobby
    except KeyError:
        return JsonResponse({}, status=501)
    
    template = {}

    # TODO ignore upper/lower case differences
    for role in roles:
        
        role = role.lower()
        if role in template:
            template[role][0] += 1
        else:
            template[role] = [1]

    if alterDB(idLobby=lobbyID, roles=str(template)) == None:
        return JsonResponse({}, status=502)

    return JsonResponse({}, status=200)

# Sec Hit game session
def gameSH(request):
    
    lobbyID = 0
    playerID = ''
    playerName = ''

    try:                
        playerID = str(ast.literal_eval(request.COOKIES['userData']).get('playerID'))
        playerName = str(ast.literal_eval(request.COOKIES['userData']).get('playerName'))
        
    # if there were no cookies, player cannot be important for current lobby
    except KeyError:
        return render(request, 'invalidGameState.html')
    
    playerCount = blockLobby(playerID)
    if playerCount == 0:
        reopenLobby(request)
        return render(request, 'invalidGameState.html')
    
    distribution = roleDistributionSH(playerCount, playerID, lobbyID)
    if len(distribution) != playerCount:
        print("Error 4")
        return render(request, 'invalidGameState.html')
    
    output = setOutputSH(playerID, playerName, distribution, playerCount, lobbyID=lobbyID)

    return render(request, 'gameSH.html', output)

# Werwolf game session
def gameWW(request):

    lobbyID = 0
    playerID = ''
    playerName = ''

    try:                
        playerID = str(ast.literal_eval(request.COOKIES['userData']).get('playerID'))
        playerName = str(ast.literal_eval(request.COOKIES['userData']).get('playerName'))
        
    # if there were no cookies, player cannot be important for current lobby
    except KeyError:
        return render(request, 'invalidGameState.html')
    
    playerCount = blockLobby(playerID)
    if playerCount == 0:
        reopenLobby(request)
        return render(request, 'invalidGameState.html')
    
    distribution = roleDistributionWW(playerID, lobbyID)
    print(distribution)
    if len(distribution) != playerCount:
        print("Error 4")
        return render(request, 'invalidGameState.html')

    
    return render(request, 'gameWW.html')
        
# alter DB with ONE of the possible parameters
def alterDB(idLobby:int=0, observation:dict=None, removeFromLobby:str=None, addToLobby:list=None, distribution:dict=None, roles:dict=None,stat:str=None, reset:bool=False):
    
    dbAltered = False
    res = None

    try:

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

            # only allow changes when game is started to: observation or reset
            if 'game' in lobby.status and (observation == None and not reset):
                return res

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

            elif roles != None:
                lobby.wwRoles = roles

            # only allow to advance in state when its not a reset
            elif stat != None:
                
                if not (stat == "standby" and "game" in lobby.status):
                    lobby.status = stat
                    print('Altered to ' + stat)

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
    
    except Exception as e:
        print(e)
        return None
    
    return res

# set game mode to game -> no new players can enter and count player
def blockLobby(playerID:int, lobbyID:int=0,):

    lobby = Lobby.objects.filter(lobbyID=lobbyID)[0]
    players = ast.literal_eval(lobby.lobbyList)

    try:
        lobbyHost = list(players.keys())[0]
    except:
        return 0

    if (lobbyHost == playerID):

        lobbyList = ast.literal_eval(alterDB(idLobby=lobbyID, stat="standby").lobbyList)
        if lobbyList == None:
            return 0    
        
        return len(lobbyList)
    
    return len(players)

# TODO make compatible with different lobbies (read from cookies?)
def reopenLobby(request):
    
    lobbyID = 0    
    lobbyList = ast.literal_eval(alterDB(idLobby=lobbyID, stat="lobby").lobbyList)
    if lobbyList == None:
        return render(request, 'invalidGameState.html')
    return lobby(request)

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

            alteredOnce = alterDB(distribution=distribution)
            alteredTwice = alterDB(stat="gameSH")
            if alteredOnce == None or alteredTwice == None:
                print("Error 3")
        else:
            print('#### Skipped!')
        
    except Exception as e:
        print(e)
        return {}

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
        
        if str(player[1]) == playerToWatch:
            
            resRole = curDistribution[player]

            if resRole == "Hitler":
                resRole = "Faschist"
            break
        else:
            print(player[1])
            print(playerToWatch)

    if alterDB(observation=[playerName, playerToWatch]) == None:
        return JsonResponse({}, status=503)
    
    return JsonResponse({playerToWatch: resRole}, status=200)

def roleDistributionWW(playerID:str, idLobby:int = 0)-> dict:

    try:
    
        lobby = Lobby.objects.filter(lobbyID=idLobby)[0]

        roles = ast.literal_eval(lobby.wwRoles)
        players = ast.literal_eval(lobby.lobbyList)
        distribution = ast.literal_eval(lobby.roleDistribution)
        gameState = lobby.status

        # only player One should be able to start the game
        lobbyHost = list(players.keys())[0]
        
        if (lobbyHost == playerID) and (gameState == 'standby'):

            distribution = {}

            for role in roles:

                while roles[role][0] != 0:

                    currentPlayer = random.choice(list(players.items()))
                    distribution[currentPlayer] = role

                    del players[currentPlayer[0]]
                    roles[role][0] -= 1

            alteredOnce = alterDB(distribution=distribution)
            alteredTwice = alterDB(stat="gameWW")
            if alteredOnce == None or alteredTwice == None:
                print("Error 3")

        else:
            print('#### Skipped!')
        
    except Exception as e:
        print(e)
        return {}

    return distribution

def outputWW()-> dict:
    pass