import os
import sys
from lxml import etree, objectify
from tests import sclparser
from iec import deviceparser

tcpPort = 102

def isIp_in_file(filename, ied_ip):
    if ied_ip in sclparser.get_ip_list(filename):
        return True
    else:
        return False

def isConnect(ied_ip):
    if deviceparser.checkConnected(ied_ip):
        return True
    else:
        return False

def isLNodesEqual(filename, ied_ip):
    ied = sclparser.getIEDbyIp(filename, ied_ip)
    scl_list = sclparser.getLNlist(ied)
    device_list = deviceparser.getLNlist_fromIED(ied_ip)

    for lnode in scl_list:
        if sclparser.get_Pretty_LNlist(lnode) not in device_list:
            print("Error on ", lnode.sourceline, "line")
            return False
    return True
