####################
#
#    Acorn Game
#    CPS375 Project
#
#    Michael Aboff
#    mwaboff (at) gmail.com
#
####################

import socket
from AcornHelp import *


state = False    
grid = ''

def sendJoin(s):
    """
    Sends a JOIN message to the server.
    """
    debugPrint("FUNCTION AcornClient.sendJoin()")
    debugPrint("Attempting to send JOIN message to server")
    msg(s, "00010000")
    listen(s, 'JOIN')
    
def sendMove(s, move):
    """
    Sends correct data to server indicating movement, based on player input.
    """
    debugPrint("FUNCTION AcornClient.sendMove()")
    m = '0100'
    f = '00'
    debugPrint("Attempting to send MOVE (%s) message to server" % move)
    if move == 'up':
        msg(s, m+f+'00')
    elif move == 'down':
        msg(s, m+f+'01')
    elif move == 'left':
        msg(s, m+f+'10')
    elif move == 'right':
        msg(s, m+f+'11')
    listen(s, 'MOVE')
    
    
def listen(s, waitfor='nothing in particular'):
    """
    Listens for server data.
    """
    debugPrint("FUNCTION AcornClient.listen()")
    debugPrint("Waiting on message for %s" % waitfor)
    buff = s.recv(1024)
    params = readMessage(buff)
    if params == None:
        debugPrint("no message :(")
        s.close()
    elif params[0] == 'ACKM':
        if waitfor == 'JOIN':
            debugPrint("Recieved ACKM message for JOIN")
            listen(s, 'STRT')
        elif waitfor == 'MOVE':
            debugPrint("Recieved ACKM message for MOVE")
            parseMoveACKM(s, params)
    elif params[0] == 'STRT':
        state = True
        genGrid(params[3])
        listenMove(s)
    elif params[0] == 'OVER':
        s.close()
        gameOver(s, params)
        
def gameOver(s, params):
    """
    Runs GameOver sequence.
    """
    debugPrint("FUNCTION AcornClient.gameOver()")
    scoreOWN = int(params[3][:8], 2)
    scoreTOP = int(params[3][8:16], 2)
    if scoreOWN == scoreTOP:
        print("YOU HAVE WON :) You collected %d acorns!\nGAME OVER!!!" % scoreOWN)
    else:
        print("YOU HAVE LOST :( You collected %d acorns! The winner collected %d acorns!" % (scoreOWN, scoreTOP))
    
def parseMoveACKM(s, params):
    """
    Parses Server response to player's movement.
    """
    debugPrint("FUNCTION AcornClient.parseMoveACKM()")
    if params[2] == '00':
        debugPrint("RECIEVED Acorn! :D")
        print('You have found an Acorn!')
    elif params[2] == '01':
        debugPrint("RECIEVED No Acorn D:")
    listenMove(s)
    
def listenMove(s):
    """
    Listens for player input.
    """
    debugPrint("FUNCTION AcornClient.listenMove()")
    print(grid)
    loop = True
    while loop:
        move = input(">>> ").lower()
        if move in ['w']:
            loop = False
            sendMove(s, 'up')
        elif move in ['s']:
            loop = False
            sendMove(s, 'down')
        elif move in ['d']:
            loop = False
            sendMove(s, 'right')
        elif move in ['a']:
            loop = False
            sendMove(s, 'left')
        else:
            print("Please choose either: 'up', 'down', 'left', or 'right'. Thank you.")    # In case the user is trying to break the system :(
            debugPrint("User input an unknown direction: %s" % move, 1)
    
def genGrid(seed):
    """
    Generates playing field.
    """
    global grid
    debugPrint("FUNCTION AcornClient.printGrid()")
    print(seed)
    debugPrint("Attempting to create Grid from the input: %s" % str(seed))
    numcolumns = conversion.index(seed[:4])
    numrows = conversion.index(seed[4:8])
    acornlocation = []
    count = 0
    newloc = ''
    for bit in seed[8:]:
        count += 1
        newloc += bit
        if count >= 8:
            count = 0
            acornlocation.append((conversion.index(newloc[:4]), conversion.index(newloc[4:])))
            newloc = ''
    try:
        acornlocation.remove((0,0))
    except:
        pass
    debugPrint("Determined that there are: %s columns | %s rows. Acorns are at locations: %s" % (numcolumns, numrows, str(acornlocation)))
    
    grid = ''
    for row in range(numrows):
        grid += '\n'
        for col in range(numcolumns):
            if (col, row) in acornlocation:
                grid += ' a'
            else:
                grid += ' x'
    print(grid)
    
def main():
    HOST = 'localhost'
    PORT = 9999
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST,PORT))

    sendJoin(s)

main()
