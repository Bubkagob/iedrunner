import sys
import traceback
from iec import *

tcpPort = 102
ip = '127.0.0.1'
def observer():
    con = iec61850.IedConnection_create()
    timeout = iec61850.IedConnection_setConnectTimeout(con, 2000)
    error = iec61850.IedConnection_connect(con, ip, tcpPort)
    state = iec61850.IedConnection_getState(con)


    if (error == iec61850.IED_ERROR_OK):
        print(state)
        [deviceList, error] = iec61850.IedConnection_getLogicalDeviceList(con)
        print(deviceList)
        iec61850.LinkedList_printStringList(deviceList)
        #device = iec61850.LinkedList_get(deviceList, 0)
        device = iec61850.LinkedList_getNext(deviceList)
        size = iec61850.LinkedList_size(deviceList)
        print("LDevices: %s" % size)
        while device: #Iterate over each device from deviceList
            LD_name = iec61850.toCharP(device.data)
            print("LD: %s " % LD_name)
            [logicalNodes, error] = iec61850.IedConnection_getLogicalDeviceDirectory(con, iec61850.toCharP(device.data))
            lnode = iec61850.LinkedList_getNext(logicalNodes)
            while lnode:#Iterate over each node from LNodeList
                LN_name = iec61850.toCharP(lnode.data)
                print("LN: %s ==== > %s" % (LN_name, LD_name))
                #Working with Data Objects
                [dataObjects, error] = iec61850.IedConnection_getLogicalNodeDirectory(con, LD_name+'/'+LN_name, iec61850.ACSI_CLASS_DATA_OBJECT)
                dobject = iec61850.LinkedList_get(dataObjects, 0)
                iIndex = 1
                while dobject:
                    print(iec61850.toCharP(dobject.data), "-----OBJ------>" , iIndex)
                    dobject = iec61850.LinkedList_get(dataObjects, iIndex)
                    iIndex += 1
                #Working with Data Sets
                [dataSets, error] = iec61850.IedConnection_getLogicalNodeDirectory(con, LD_name+'/'+LN_name, iec61850.ACSI_CLASS_DATA_SET)
                dataSet = iec61850.LinkedList_getNext(dataSets)
                size = iec61850.LinkedList_size(dataSets)
                print("Datasets: %s" % size)
                iIndex = 1
                while dataSet:
                    DS_name = iec61850.toCharP(dataSet.data)
                    print(DS_name, "----------->" , iIndex)
                    dataSet = iec61850.LinkedList_get(dataSets, iIndex)
                    isDel = None
                    [dataSetMembers, error] = iec61850.IedConnection_getDataSetDirectory(con, LD_name+'/'+LN_name+'.'+DS_name, isDel)
                    if isDel:
                        print("Dataset: %s(deletable)" %DS_name)
                    else:
                        print("Dataset: %s(not deletable)" %DS_name)
                    dataSetMemberRef = iec61850.LinkedList_getNext(dataSetMembers)
                    size = iec61850.LinkedList_size(dataSetMembers)
                    print("DatasetMembers: %s" % size)
                    dsIndex = 1
                    while dataSetMemberRef:
                        DSMember_name = iec61850.toCharP(dataSetMemberRef.data)
                        print(DSMember_name, "----DS------->" , dsIndex)
                        dataSetMemberRef = iec61850.LinkedList_get(dataSetMembers, dsIndex)
                        dsIndex += 1
                    iIndex += 1
                    iec61850.LinkedList_destroy(dataSetMembers)
                iec61850.LinkedList_destroy(dataSets)
                #Working with Reports
                [reports, error] = iec61850.IedConnection_getLogicalNodeDirectory(con, LD_name+'/'+LN_name, iec61850.ACSI_CLASS_BRCB)
                size = iec61850.LinkedList_size(reports)
                print("Reports: %s" % size)
                report = iec61850.LinkedList_getNext(reports)
                repIndex = 1
                while report:
                    Report_name = iec61850.toCharP(report.data)
                    print("Report name is : %s " % Report_name)
                    report = iec61850.LinkedList_get(reports, repIndex)
                    repIndex += 1
                iec61850.LinkedList_destroy(reports)
                lnode = iec61850.LinkedList_getNext(lnode)
            iec61850.LinkedList_destroy(dataObjects)
            iec61850.LinkedList_destroy(logicalNodes)
            device = iec61850.LinkedList_getNext(device)
        iec61850.LinkedList_destroy(deviceList)
        iec61850.IedConnection_close(con)
    else:
        print ("Connection error status")
        sys.exit(-1)

    iec61850.IedConnection_destroy(con)
    print("Client OK")



if __name__ == "__main__":
    try:
    	observer()

    except:
    	print ("Error :")
    	traceback.print_exc(file=sys.stdout)
    	sys.exit(-1)
