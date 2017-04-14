import argparse
import time
from iec import *
import subprocess

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
                if req[0][-1:]=='f' and req[1] in ['f32', 'f64']:
                    if not (float(req[2]) == clt.readFloat(req[0])):
                        print("ReadFloat trouble   -   -   ->",req[0],req[2])
                elif req[0][-1:]=='f' and req[1] in ['int8', 'uint8', 'int16', 'uint16', 'int32', 'uint32']:
                    if not (float(req[2]) == clt.readInt32(req[0])):
                        print("ReadInt trouble  -   -   ->",req[0],req[2])
                elif req[0][-1:]=='t' and req[1] in ['uint64']:
                    if not (float(req[2]) == clt.readTimeStamp(req[0])):
                        print("Read Timestampt trouble  -   -   ->",req[0],req[2])
                elif req[0][-1:]=='q' and req[1] in ['uint16']:
                    if not (int(req[2]) == clt.readQuality(req[0])):
                        print("Read Quality trouble  -   -   ->",req[0],req[2])
            print("Checking finished")
        except Exception as e:
            print('!!!234!         Exception: ', str(e) )


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
        clt = client.iecClient()
        checker(parser, clt)
        clt.stop()
    except ValueError:
        print('IP is invalid:' )
    except Exception as e:
        print('!!!!  Exception: ', str(e) )
