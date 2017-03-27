import os
import sys
from lxml import etree, objectify

from sclparser import get_ip_list, getIEDbyIp, getLNlist
from deviceparser import checkConnected, getLNlist_fromIED

tcpPort = 102

def get_Pretty_LNlist(lnode):
    if 'prefix' in lnode.attrib:
        if(lnode.get('prefix')):
            return (lnode.get('prefix')+lnode.get('lnClass')+lnode.get('inst'))
        else:
            return (lnode.get('lnClass')+lnode.get('inst'))
    else:
        return lnode.get('lnClass')

def isIp_in_file(filename, ied_ip):
    if ied_ip in get_ip_list(filename):
        return True
    else:
        return False

def isConnect(ied_ip):
    if checkConnected(ied_ip):
        return True
    else:
        return False

def isLNodesEqual(filename, ied_ip):
    ied = getIEDbyIp(filename, ied_ip)
    scl_list = getLNlist(ied)
    device_list = getLNlist_fromIED(ied_ip)

    for lnode in scl_list:
        if get_Pretty_LNlist(lnode) not in device_list:
            print("Error on ", lnode.sourceline, "line")
            return False
            
    return True
