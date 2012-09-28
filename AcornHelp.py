####################
#
#    Acorn Game - Module
#    CPS375 Project
#
#    Michael Aboff
#    mwaboff (at) gmail.com
#
####################

global debug, prefixmap, conversion
debug = False

prefixmap = {
    '0001':'JOIN',
    '0010':'ACKM',
    '0011':'STRT',
    '0100':'MOVE',
    '0101':'OVER',
    }

conversion = ['0000','0001','0010','0011','0100','0101','0111','1000','1001','1010','1011','1100','1101','1111']


def debugPrint(info, e=0):
    """
    Using this function lets us easily turn off debug mode by modifying the value of debug in this module :D
    """
    if debug == True and e == 0:
        if type(info) == str:
            print("=DEBUG= "+info)
    if e == 1:
        print("!! ERROR: "+info)

def msg(s, data):
    """
    An attempt to get a centralized place to send out the info.
    """
    debugPrint("FUNCTION AcornHelp.msg()")
    debugPrint("SENDING: %s" % data)
    data = '0b'+data+'00000000'
    message = data.encode()
    s.send(message)
    

def readMessage(data):
    """
    This might do a little too much parsing...
    """
    debugPrint("FUNCTION AcornHelp.readMessage()")
    data = data.decode()
    data = str(data)[2:]
    debugPrint("RECIEVING: %s" % data)
    try:
        dtype = data[:4]    # This section tries to break up the binary into it's proper segments to make it mad easy
        dflag = data[4:6]
        ddata = data[6:8]
        num0 = 0
        counter = 0
        realcount = 0
        for miscdata in data[8:]:    # Here is to try to figure out where the actual data ends after the two data bits
            if num0 < 8:
                counter += 1
                if miscdata == '0':
                    num0 += 1
                elif miscdata == '':
                    debugPrint("Failure in determining the end of the information (no 8 consequative 0's): %s" % data[9:], 1)
                else:
                    num0 = 0
        if num0 == 8:
            dmisc = data[8:8+counter]
        debugPrint("PARSED data. TYPE = %s | FLAG = %s | DATA = %s | MISC = %s" % (dtype, dflag, ddata, dmisc))
    except:
        debugPrint("Failure when parsing recieved data", 1)
    if dtype in prefixmap:
        debugPrint("PARSED Known data type: %s" % prefixmap[dtype])
        return prefixmap[dtype], dflag, ddata, dmisc
    else:
        debugPrint("Unknown type prefix: %s" % dtype, 1)
        return
