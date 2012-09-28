####################
#
#    Acorn Game - Server
#    CPS375 Project
#
#    Michael Aboff
#    mwaboff (at) gmail.com
#
####################


import socket, random
from AcornHelp import *

# Setting default values
gamestate = False
squirrels = {}
needed = 1
gridcol = 10
gridrow = 10
acorn = {'amount':5, 'locations':[]}

def listener(conn):
    """
    Listens to incoming data from connected clients.
    """
    debugPrint("FUNCTION AcornServer.listener()")
    while True:
        try:
            data = conn.recv(1024)
            message = readMessage(data)
            parser(conn, message)
        except socket.error:
            conn.close()
            print("Connection closed")
            break

def parser(conn, data):
    """
    Parses incoming data to determine data type.
    """
    debugPrint("FUNCTION AcornServer.parser()")
    debugPrint("Gamestate is %s" % str(gamestate))
    if gamestate == False:
        if data[0] == 'JOIN':
            debugPrint("JOINED: %s" % str(conn.getpeername()))
            addSquirrel(conn, data)
    else:
        if data[0] == 'MOVE':
            moveSquirrel(conn, data)
        
def addSquirrel(conn, data):
    """
    Add players and set default positions.
    """
    debugPrint("FUNCTION AcornServer.addSquirrel()")
    squirrels[conn] = {'location':[0,0], 'acorns':0}
    msg(conn, '00100000')    # Send ACKM to Client
    if len(squirrels) == needed:
        sendSTRT()

def moveSquirrel(conn, data):
    """
    Parses the movement data and sets the squirrel's position.
    """
    debugPrint("FUNCTION AcornServer.moveSquirrel()")
    t = '0010'
    f = '00'
    tomove = squirrels[conn]['location']
    if data[2] == '00':
        tomove[1] -= 1
        if tomove[1] < 0:
            tomove[1] = gridcol-1
    elif data[2] == '01':
        tomove[1] += 1
        if tomove[1] > gridcol-1:
            tomove[1] = 0
    elif data[2] == '10':
        tomove[0] -= 1
        if tomove[0] < 0:
            tomove[0] = gridrow-1
    elif data[2] == '11':
        tomove[0] += 1
        if tomove[0] > gridrow-1:
            tomove[0] = 0
    msg(conn, t+f+checkAcorn(conn))
    debugPrint("MOVED Squirrel %s to %s" % (conn.getpeername(), str(tomove)))
    checkGameOver()
    
def checkGameOver():
    """
    Checks amount of acorns remaining, if none are left, the game is over.
    """
    debugPrint("FUNCTION AcornServer.checkGameOver()")
    debugPrint("CHECK for game over conditions (no more acorns)")
    if acorn['amount'] <= 0 and len(acorn['locations']) == 0:
        debugPrint("CHECK NO MORE ACORNS: game over conditions are met")
        gamestate = False
        topscore = 0
        
        for player in squirrels.keys():
            if topscore < squirrels[player]['acorns']:
                topscore = squirrels[player]['acorns']
        bintopscore = bin(topscore)[2:]
        bintopscore = '0'*(8-len(bintopscore))+bintopscore
        
        for player in squirrels.keys():
            score = squirrels[player]['acorns']
            debugPrint("Player %s has has %s acorns" % (player.getpeername(), score))
            binscore = bin(score)[2:]
            binscore = '0'*(8-len(binscore))+binscore
            msg(player, "01010000"+binscore+bintopscore)
            player.close()
        debugPrint("GAME OVER: shutting down server")

def sendSTRT():
    """
    Tells clients that the game has begun!
    """
    global gamestate
    gamestate = True
    debugPrint("FUNCTION AcornServer.sendSTRT()")
    s = '0011'
    f = '00'
    d = '00'
    grid = genGrid()
    for squirrel in squirrels.keys():
        msg(squirrel, s+f+d+grid)
    debugPrint("START game")
        
def genGrid():
    """
    Generates playing field.
    """
    debugPrint("FUNCTION AcornServer.genGrid()")
    grid = conversion[gridcol]+conversion[gridrow]
    for a in range(acorn['amount']):
        col=0
        row=0
        while col == 0 and row == 0:
            col = random.randint(0,gridcol-1)
            row = random.randint(0,gridrow-1)
        colcoord = conversion[col]
        rowcoord = conversion[row]
        grid += colcoord+rowcoord
        acorn['locations'].append((col,row))
    debugPrint("Generated Grid and recorded the locations of the acorns: %s" % str(acorn['locations']))
    return grid

def checkAcorn(conn):
    """
    Determines if the player has found an acorn.
    """
    debugPrint("FUNCTION AcornServer.checkAcorn()")
    location = squirrels[conn]['location']
    debugPrint("Checking to see if location %s holds an acorn" % str(location))
    if tuple(location) in acorn['locations']:
        acorn['amount'] -= 1
        acorn['locations'].remove(tuple(location))
        squirrels[conn]['acorns'] += 1
        return '00'
    return '01'

def main():
    debugPrint("FUNCTION AcornServer.main()")
    HOST = ''     
    PORT = 9999
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen(10)
    
    conn, addr = s.accept()
    listener(conn)
    
    s.close()

main()
