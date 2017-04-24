import argparse
import time
from iec import *
import subprocess



def line_requester(req):
    if req[0][-1:]=='f' and req[1] in ['f32', 'f64']:
        if not (float(req[2]) == clt.readFloat(req[0])):
            print("ReadFloat trouble   -   -   ->",req[0],req[2])
    elif req[0][-1:]=='f' and req[1] in ['int8', 'uint8', 'int16', 'uint16', 'int32', 'uint32']:
        if not (float(req[2]) == clt.readInt32(req[0])):
            print("ReadInt trouble  -   -   ->",req[0],req[2])
    elif req[0][-5:]=='stVal' and req[1] in ['uint8',  'uint16',  'uint32',  'f32', 'f64']:
        answer = clt.readBoolean(req[0])
        if req[2]=='0':
            if answer:
                print("Read Boolean trouble  -   -   ->",req[0],req[2])
            else:
                print("ok 1")
        else:
            if not answer:
                print(answer)
                print("ok 3")
                print("Read Boolean trouble  -   -   ->",req[0],req[2])
            else:
                print(answer)
                print("ok 2")
    elif req[0][-1:]=='t' and req[1] in ['uint64']:
        if req[2] == "now":
            print("Now variable ", clt.readTimeStamp(req[0], 'iec61850.IEC61850_FC_ST'))
        else:
            print("not Now variable = = ", clt.readTimeStamp(req[0]))
    elif req[0][-1:]=='q' and req[1] in ['uint16']:
        if not (int(req[2]) == clt.readQuality(req[0])):
            print("Read Quality trouble  -   -   ->",req[0],req[2])



def sasClient(parser):
    client = parser.parse_args().client
    connection = parser.parse_args().conn
    filename = parser.parse_args().file
    repeat = parser.parse_args().repeat
    timeout = parser.parse_args().timeout
    cmd = client+' --connection='+connection+' --file='+filename+' --repeat='+repeat +' --timeout='+timeout
    proc = subprocess.run(cmd, shell = True)
    time.sleep(1)



def checker(parser, client):
    print("-"*60)
    print("Trying to check values...")
    with open(parser.parse_args().file) as f:
        requests = [request.split() for request in f]
        try:
            gen = (request for request in requests if len(request) == 3)
            for req in gen:
                line_requester(req)
            print("Checking finished")
        except Exception as e:
            print('!!!Exception!!!!!         Exception: ', str(e) )


def inputParse():
    parser = argparse.ArgumentParser(prog = 'test')
    parser.add_argument('-clt', '--client', dest = 'client' , required=True, help='shm client app\'s name')
    parser.add_argument('-con', '--connection', dest='conn', required=True, help='shm connection name')
    parser.add_argument('-f', '--file', required=True, help='Filename')
    parser.add_argument('-r', '--repeat', required=False, default='1',help='repeat times')
    parser.add_argument('-t', '--timeout', required=False, default='1000', help='Timeout in microseconds')
    return parser



'''
#############################################################################
#                                  main                                     #
#############################################################################
'''

if __name__ == '__main__':
    parser = inputParse()
    try:
        sasClient(parser)
        clt = client.IecClient()
        checker(parser, clt)
        clt.stop()
    except ValueError:
        print('IP is invalid:' )
    except Exception as e:
        print('!!!!  Exception: ', str(e) )
