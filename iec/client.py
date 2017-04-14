import sys
import threading
import traceback
import getch
import iec61850


running = 1
class iecClient():
    def __init__(self, ip='127.0.0.1', tcpPort=102):
        try:
            self.__con = iec61850.IedConnection_create()
            self.__timeout = iec61850.IedConnection_setConnectTimeout(self.__con, 2000)
            self.__error = iec61850.IedConnection_connect(self.__con, ip, tcpPort)
            if (self.__error == iec61850.IED_ERROR_OK):
                running = 1
        except Exception as e:
            print('Connection exception: ', str(e))
            running = 0
            #sys.exit(-1)

    def getConnectionState(self):
        return iec61850.IedConnection_getState(self.__con)

    def getIEDnameList(self):
        iednames = []
        [deviceList, error] = iec61850.IedConnection_getLogicalDeviceList(self.__con)
        device = iec61850.LinkedList_getNext(deviceList)
        while device: #Iterate over each device from deviceList
            iednames.append(iec61850.toCharP(device.data))
            device = iec61850.LinkedList_getNext(device)
        return iednames

    def readAttributes(self):
        rcb = self.__rcb
        print("*"*100)
        isEnabled = iec61850.ClientReportControlBlock_getRptEna(rcb)
        print("Enabled:",isEnabled)
        reserverTime = iec61850.ClientReportControlBlock_getResvTms(rcb)
        print("reserverTime:",reserverTime)
        CBref = iec61850.ClientReportControlBlock_getObjectReference(rcb)
        print("CBref:",CBref)
        reportID = iec61850.ClientReportControlBlock_getRptId(rcb)
        print("reportID:",reportID)
        dsRef = iec61850.ClientReportControlBlock_getDataSetReference(rcb)
        print("dsRef:",dsRef)
        trgOpt = iec61850.ClientReportControlBlock_getTrgOps(rcb)
        print("trgOpt:",trgOpt)
        bufTime = iec61850.ClientReportControlBlock_getBufTm(rcb)
        print("bufTime:",bufTime)
        isBuffered = iec61850.ClientReportControlBlock_isBuffered(rcb)
        print("isBuffered:",isBuffered)
        confRev = iec61850.ClientReportControlBlock_getConfRev(rcb)
        print("confRev:",confRev)
        intPeriod = iec61850.ClientReportControlBlock_getIntgPd(rcb)
        print("intPeriod:",intPeriod)
        owner = iec61850.ClientReportControlBlock_getOwner(rcb)
        print("Owner:",iec61850.MmsValue_getBitStringAsInteger(owner))
        gi = iec61850.ClientReportControlBlock_getGI(rcb)
        print("GI:",gi)
        isReserved = iec61850.ClientReportControlBlock_getResv(rcb)
        print("isReserved:",isReserved)
        entryTime = iec61850.ClientReportControlBlock_getEntryTime(rcb)
        print("entryTime:",entryTime)
        print("-"*100)

    def run(self):
        print("Running...")
        global running
        while running:
            print(running)
            pressedKey = getch.getch()
            if pressedKey == 'q':
                print("Q was pressed")
                running = 0
                self.stop()
            elif pressedKey == 'x':
                print("Exiting....")
                sys.exit()
            elif pressedKey == 'g':
                print("GetAttributes....")
                self.getRCB()
            elif pressedKey == 'r':
                print("Read Attributes....")
                self.readAttributes()
            elif pressedKey == 'i':
                print("Install report receiver....")
                self.installHandler()
            elif pressedKey == 'e':
                print("Enabling Report....")
                self.enableReport()
            elif pressedKey == 'd':
                print("Disabling Report....")
                self.disableReport()
            elif pressedKey == 't':
                print("Trigger report")
                self.triggerReport()
            elif pressedKey == 'p':
                print("Gettin DataSetDirectory...")
                self.getDataSetDirectory()
            else:
                print("Key Pressed:" + str(pressedKey))

    def readFloat(self, var):
        [floatValue, self.__error] = iec61850.IedConnection_readFloatValue(self.__con, var, iec61850.IEC61850_FC_MX)
        return floatValue

    def readInt32(self, var):
        [intValue, self.__error] = iec61850.IedConnection_readFloatValue(self.__con, var, iec61850.IEC61850_FC_MX)
        print("int8-32 Value:            ", intValue)

    def readTimeStamp(self, var):
        time = iec61850.Timestamp()
        [timeStampValue, self.__error] = iec61850.IedConnection_readTimestampValue(self.__con, var, iec61850.IEC61850_FC_MX, time)
        return iec61850.Timestamp_getTimeInMs(time)

    def readInt32(self, var):
        [intValue, self.__error] = iec61850.IedConnection_readFloatValue(self.__con, var, iec61850.IEC61850_FC_MX)
        return intValue

    def readQuality(self, var):
        [qualityValue, self.__error] = iec61850.IedConnection_readQualityValue(self.__con, var, iec61850.IEC61850_FC_MX)
        return qualityValue

    def stop(self):
        iec61850.IedConnection_close(self.__con)
        iec61850.IedConnection_destroy(self.__con)
        #sys.exit()

    def reportCallbackFunction(self, parameter, report):
        print("Report CallBack Function")
        size = iec61850.LinkedList_size(parameter)
        print("Entries count: %s" % size)
        entry = iec61850.LinkedList_getNext(parameter)
        Index = 1
        while entry:
            entry_name = iec61850.toCharP(entry.data)
            print(entry_name, "Entry------->" , Index)
            entry = iec61850.LinkedList_get(parameter, Index)
            Index += 1
        #iec61850.LinkedList_destroy(parameter)
        print("Report received!")

    def getRCB(self):
        [self.__rcb, error] = iec61850.IedConnection_getRCBValues(self.__con, "TEMPLATELD0/LLN0.BR.brcbMX0101", None)
        if (error == iec61850.IED_ERROR_OK):
            print("RCB read success")
        else:
            print("failed to read RCB")

    def getDataSetDirectory(self):
        isDel = None
        #Working with Reports:
        [self.__dataSetDirectory, error] = iec61850.IedConnection_getDataSetDirectory(self.__con, "TEMPLATELD0/LLN0.MxDs", isDel)
        if (error == iec61850.IED_ERROR_OK):
            print("OK")
            if isDel:
                print("Dataset: (deletable)")
            else:
                print("Dataset: (not deletable)")
        else:
            print ("Connection error status")
            stop()
            #sys.exit(-1)

    def installHandler(self):
        print("--------------------Install Report receiver")
        iec61850.IedConnection_installReportHandler(self.__con,
                                                    "TEMPLATELD0/LLN0.BR.brcbMX0101",
                                                    iec61850.ClientReportControlBlock_getRptId(self.__rcb),
                                                    self.reportCallbackFunction,
                                                    self.__dataSetDirectory
                                                    )

    def triggerReport(self):
        iec61850.IedConnection_triggerGIReport(self.__con, "TEMPLATELD0/LLN0.BR.brcbMX0101")

    def enableReport(self):
        print("Enabling rptEna")
        iec61850.ClientReportControlBlock_setResv(self.__rcb, True)
        iec61850.ClientReportControlBlock_setDataSetReference(self.__rcb, "TEMPLATELD0/LLN0$MxDs")
        iec61850.ClientReportControlBlock_setRptEna(self.__rcb, True)
        iec61850.ClientReportControlBlock_setGI(self.__rcb, True)
        iec61850.IedConnection_setRCBValues(self.__con, self.__rcb, iec61850.RCB_ELEMENT_GI, True)

    def disableReport(self):
        print("disable rptEna")
        iec61850.ClientReportControlBlock_setResv(self.__rcb, False)
        iec61850.ClientReportControlBlock_setRptEna(self.__rcb, False)
        iec61850.ClientReportControlBlock_setGI(self.__rcb, False)
        iec61850.ClientReportControlBlock_setGI(self.__rcb, False)
        iec61850.IedConnection_setRCBValues(self.__con, self.__rcb, iec61850.RCB_ELEMENT_GI, False)

if __name__ == "__main__":
    try:
        clt=iecClient()
        cltThread = threading.Thread(target = clt.run)
        cltThread.start()
    except:
        running = 0
        print ("Error :")
        traceback.print_exc(file=sys.stdout)
        sys.exit(-1)
