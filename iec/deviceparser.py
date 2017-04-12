import os,sys
import traceback
from iec61850 import *

tcpPort = 102

def getLNlist_fromIED(ip):
    res_list = []
    con = iec61850.IedConnection_create()
    error = iec61850.IedConnection_connect(con, ip, tcpPort)
    state = iec61850.IedConnection_getState(con)
    if (error == iec61850.IED_ERROR_OK):
        [deviceList, error] = iec61850.IedConnection_getLogicalDeviceList(con)
        device = iec61850.LinkedList_getNext(deviceList)
        size = iec61850.LinkedList_size(deviceList)
        while device: #Iterate over each device from deviceList
            [logicalNodes, error] = iec61850.IedConnection_getLogicalDeviceDirectory(con, iec61850.toCharP(device.data))
            lnode = iec61850.LinkedList_getNext(logicalNodes)
            while lnode:#Iterate over each node from LNodeList
                LN_name = iec61850.toCharP(lnode.data)
                res_list.append(LN_name)
                lnode = iec61850.LinkedList_getNext(lnode)
            iec61850.LinkedList_destroy(logicalNodes)
            device = iec61850.LinkedList_getNext(device)
        iec61850.LinkedList_destroy(deviceList)
        iec61850.IedConnection_close(con)
    else:
        print ("Connection error")
        sys.exit(-1)
    iec61850.IedConnection_destroy(con)
    return res_list


def checkConnected(ip):
    try:
        con = iec61850.IedConnection_create()
        error = iec61850.IedConnection_connect(con, ip, tcpPort)
        state = iec61850.IedConnection_getState(con)
        if (error == iec61850.IED_ERROR_OK):
            iec61850.IedConnection_destroy(con)
            return True
        else:
            iec61850.IedConnection_destroy(con)
            return False
    except Exception:
        print("Connection error")
        sys.exit(-1)
    iec61850.IedConnection_destroy(con)



tcpPort = 102
#ip = '192.168.137.34'
#ip = '10.151.12.94'
def run_client(ip, dt, var):
    print(ip, dt, var)
    con = iec61850.IedConnection_create()
    timeout = iec61850.IedConnection_setConnectTimeout(con, 2000)
    error = iec61850.IedConnection_connect(con, ip, tcpPort)
    state = iec61850.IedConnection_getState(con)
    if (error == iec61850.IED_ERROR_OK and state):
        print("Good connection")
        if dt == 'b':
            [booleanValue, error] = iec61850.IedConnection_readBooleanValue(con, var, iec61850.IEC61850_FC_ST)
            print("booleanValue:    ", booleanValue)
        elif dt == 'f':
            [analogValue, error] = iec61850.IedConnection_readFloatValue(con, var, iec61850.IEC61850_FC_MX)
            print("Analog Value:            ", analogValue)
        elif dt == 't':
            time = iec61850.Timestamp()
            [timeStampValue, error] = iec61850.IedConnection_readTimestampValue(con, var, iec61850.IEC61850_FC_MX, time)
            print("timeStampValue:  ", iec61850.Timestamp_getTimeInSeconds(time))
        elif dt == 'q':
            [qualityValue, error] = iec61850.IedConnection_readQualityValue(con, var, iec61850.IEC61850_FC_MX)
            print("qualityValue:    ", qualityValue)
    else:
        print ("Connection error status")
        sys.exit(-1)

    iec61850.IedConnection_destroy(con)
    print("Client OK")
