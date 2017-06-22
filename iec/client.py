import sys
import threading
import traceback
import getch
import iec61850
from ctypes import *


running = 1
class IecClient():
    def __init__(self, ip='127.0.0.1', tcpPort=102):
        try:
            self.__con = iec61850.IedConnection_create()
            self.__timeout = iec61850.IedConnection_setConnectTimeout(self.__con, 2000)
            self.__error = iec61850.IedConnection_connect(self.__con, ip, tcpPort)
            if (self.__error == iec61850.IED_ERROR_OK):
                running = 1
            else:
                print("ошибка", self.__error)
        except Exception as e:
            print('Connection exception: ', str(e))

    def get_connection_state(self):
        return iec61850.IedConnection_getState(self.__con)

    def get_ied_ld_names(self):
        iednames = []
        [deviceList, error] = iec61850.IedConnection_getLogicalDeviceList(self.__con)
        device = iec61850.LinkedList_getNext(deviceList)
        while device: # Iterate over each device from deviceList
            iednames.append(iec61850.toCharP(device.data))
            device = iec61850.LinkedList_getNext(device)
        iec61850.LinkedList_destroy(deviceList)
        return iednames

    def get_name_of(self, obj):
        return iec61850.toCharP(obj.data)

    def get_ld_list(self):
        ld_list = []
        [ldList, self.__error] = iec61850.IedConnection_getLogicalDeviceList(self.__con)
        device = iec61850.LinkedList_getNext(ldList)
        while device:  # Iterate over each device from deviceList
            ld_list.append(device)
            device = iec61850.LinkedList_getNext(device)
        # iec61850.LinkedList_destroy(ldList)
        return ld_list

    def get_ln(self, ld, lname):
        return iec61850.LogicalDevice_getLogicalNode(ld, lname)

    def get_ln_list_from_ld(self, ld):
        ln_list = []
        [lNodes, self.__error] = iec61850.IedConnection_getLogicalDeviceDirectory(self.__con, iec61850.toCharP(ld.data))
        lnode = iec61850.LinkedList_getNext(lNodes)
        while lnode:#Iterate over each node from LNodeList
            ln_list.append(lnode)
            lnode = iec61850.LinkedList_getNext(lnode)
        #iec61850.LinkedList_destroy(lNodes)
        return ln_list

    def get_dobject_names(self, ld, ln):
        [dataObjects, self.__error] = iec61850.IedConnection_getLogicalNodeDirectory(self.__con, self.get_name_of(ld)+'/'+self.get_name_of(ln), iec61850.ACSI_CLASS_DATA_OBJECT)
        dobject = iec61850.LinkedList_get(dataObjects, 0)
        iIndex = 1
        do_names = []
        while dobject:
            do_names.append(iec61850.toCharP(dobject.data))
            dobject = iec61850.LinkedList_get(dataObjects, iIndex)
            iIndex += 1
        iec61850.LinkedList_destroy(dataObjects)
        return do_names

    def get_ln_names(self, ld):
        ln_names = []
        [logicalNodes, self.__error] = iec61850.IedConnection_getLogicalDeviceDirectory(self.__con, iec61850.toCharP(ld.data))
        lnode = iec61850.LinkedList_getNext(logicalNodes)
        while lnode:#Iterate over each node from LNodeList
            ln_names.append(iec61850.toCharP(lnode.data))
            lnode = iec61850.LinkedList_getNext(lnode)
        iec61850.LinkedList_destroy(logicalNodes)
        return ln_names

    def get_varlist_fc_by_ld_lnname(self, iedldlnname):
        var_dict = {}
        [variables, self.__error] = iec61850.IedConnection_getLogicalNodeVariables(self.__con, iedldlnname)
        variable = iec61850.LinkedList_get(variables, 0)
        vIndex = 1
        while variable:
            name = iec61850.toCharP(variable.data)
            fc_name = name.split("$", 1)[0]
            if '$' in name:
                var_name = name.split("$",1)[1]
                var_name = var_name.replace("$", ".")
                #print(fc_name, "-----FC------>" , vIndex)
                var_dict[iedldlnname+'.'+var_name]=fc_name
            variable = iec61850.LinkedList_get(variables, vIndex)
            vIndex += 1
        iec61850.LinkedList_destroy(variables)
        return var_dict

    def get_var_dict_fc_by_ied(self):
        var_dict = {}
        [deviceList, self.__error] = iec61850.IedConnection_getLogicalDeviceList(self.__con)
        device = iec61850.LinkedList_getNext(deviceList)
        while device:
            ld_inst = iec61850.toCharP(device.data)
            [logicalNodes, self.__error] = iec61850.IedConnection_getLogicalDeviceDirectory(self.__con, iec61850.toCharP(device.data))
            lnode = iec61850.LinkedList_getNext(logicalNodes)
            while lnode:
                ln_name = iec61850.toCharP(lnode.data)
                [variables, self.__error] = iec61850.IedConnection_getLogicalNodeVariables(self.__con, ld_inst+'/'+ln_name)
                variable = iec61850.LinkedList_get(variables, 0)
                vIndex = 1
                while variable:
                    name = iec61850.toCharP(variable.data)
                    fc_name = name.split("$", 1)[0]
                    if '$' in name:
                        var_name = name.split("$",1)[1]
                        var_name = var_name.replace("$", ".")
                        #print(fc_name, "-----FC------>" , vIndex)
                        var_dict[ld_inst+'/'+ln_name+'.'+var_name]=fc_name
                    variable = iec61850.LinkedList_get(variables, vIndex)
                    vIndex += 1
                iec61850.LinkedList_destroy(variables)
                lnode = iec61850.LinkedList_getNext(lnode)
            iec61850.LinkedList_destroy(logicalNodes)
            device = iec61850.LinkedList_getNext(device)
        iec61850.LinkedList_destroy(deviceList)
        return var_dict

    def get_IEC61850_FC_by_fc(self, fcname):
        if fcname == 'ST':
            return iec61850.IEC61850_FC_ST
        if fcname == 'MX':
            return iec61850.IEC61850_FC_MX
        if fcname == 'SP':
            return iec61850.IEC61850_FC_SP
        if fcname == 'SV':
            return iec61850.IEC61850_FC_SV
        if fcname == 'CF':
            return iec61850.IEC61850_FC_CF
        if fcname == 'DC':
            return iec61850.IEC61850_FC_DC
        if fcname == 'SG':
            return iec61850.IEC61850_FC_SG
        if fcname == 'SE':
            return iec61850.IEC61850_FC_SE
        if fcname == 'SR':
            return iec61850.IEC61850_FC_SR
        if fcname == 'OR':
            return iec61850.IEC61850_FC_OR
        if fcname == 'BL':
            return iec61850.IEC61850_FC_BL
        if fcname == 'EX':
            return iec61850.IEC61850_FC_EX
        if fcname == 'CO':
            return iec61850.IEC61850_FC_CO
        if fcname == 'US':
            return iec61850.IEC61850_FC_US
        if fcname == 'MS':
            return iec61850.IEC61850_FC_MS
        if fcname == 'RP':
            return iec61850.IEC61850_FC_RP
        if fcname == 'BR':
            return iec61850.IEC61850_FC_BR
        if fcname == 'LG':
            return iec61850.IEC61850_FC_LG
        else:
            print('FC name not in Library')

    def get_vartype_by_fc(self, varname, fc):
        [obj, self._error] = iec61850.IedConnection_readObject(self.__con, varname, self.get_IEC61850_FC_by_fc(fc))
        objtype = iec61850.MmsValue_getTypeString(obj)
        iec61850.MmsValue_delete(obj)
        return objtype

    def get_varlist_bytype_by_ld_lnname(self, iedldlnname):
        var_dict = {}
        var_dict_fc = self.get_varlist_fc_by_ld_lnname(iedldlnname)
        for variable in var_dict_fc:
            var_dict[variable]=self.get_vartype_by_fc(variable, var_dict_fc[variable])
        return var_dict

    def get_rcbr_list_by_ldname(self, ldname):
        rc_names = []
        [reports, self.__error] = iec61850.IedConnection_getLogicalNodeDirectory(self.__con, ldname+'/LLN0', iec61850.ACSI_CLASS_BRCB)
        report = iec61850.LinkedList_getNext(reports)
        repIndex = 1
        while report:
            rc_names.append(iec61850.toCharP(report.data))
            report = iec61850.LinkedList_get(reports, repIndex)
            repIndex += 1
        iec61850.LinkedList_destroy(reports)
        return rc_names

    def get_rcrp_list_by_ldname(self, ldname):
        rc_names = []
        [reports, self.__error] = iec61850.IedConnection_getLogicalNodeDirectory(self.__con, ldname+'/LLN0', iec61850.ACSI_CLASS_URCB)
        report = iec61850.LinkedList_getNext(reports)
        repIndex = 1
        while report:
            rc_names.append(iec61850.toCharP(report.data))
            report = iec61850.LinkedList_get(reports, repIndex)
            repIndex += 1
        iec61850.LinkedList_destroy(reports)
        return rc_names

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
                self.get_rcb()
            elif pressedKey == 'r':
                print("Read Attributes....")
                self.readAttributes()
            elif pressedKey == 'i':
                print("Install report receiver....")
                self.install_handler()
            elif pressedKey == 'e':
                print("Enabling Report....")
                self.enable_report()
            elif pressedKey == 'd':
                print("Disabling Report....")
                self.disable_report()
            elif pressedKey == 't':
                print("Trigger report")
                self.triggerReport()
            elif pressedKey == 'p':
                print("Gettin DataSetDirectory...")
                self.getDataSetDirectory()
            else:
                print("Key Pressed:" + str(pressedKey))

    def read_boolean(self, var):
        [booleanValue, self.__error] = iec61850.IedConnection_readBooleanValue(self.__con, var, iec61850.IEC61850_FC_ST)
        return booleanValue

    def read_float(self, var, fc):
        [float_val, self.__error] = iec61850.IedConnection_readFloatValue(self.__con, var, self.get_IEC61850_FC_by_fc(fc))
        return float("{0:.3f}".format(float_val))

    def read_int32(self, var, fc):
        [intValue, self.__error] = iec61850.IedConnection_readInt32Value(self.__con, var, self.get_IEC61850_FC_by_fc(fc))
        return int(intValue)

    def read_uint32(self, var, fc):
        [intValue, self.__error] = iec61850.IedConnection_readUnsigned32Value(self.__con, var, self.get_IEC61850_FC_by_fc(fc))
        return intValue

    def read_int64(self, var, fc):
        [intValue, self.__error] = iec61850.IedConnection_readInt64Value(self.__con, var, self.get_IEC61850_FC_by_fc(fc))
        return intValue

    def read_st(self, var):
        [stValue, self.__error] = iec61850.IedConnection_readUnsigned32Value(self.__con, var, iec61850.IEC61850_FC_ST)
        print('stVal Value:\t\t', stValue)
        [st, self.__error] = iec61850.IedConnection_readObject(self.__con, var, iec61850.IEC61850_FC_ST)
        print("STVal_Type:\t\t", iec61850.MmsValue_getTypeString(st))

    def read_timestamp(self, var, fc):
        time = iec61850.Timestamp()
        [timeStampValue, self.__error] = iec61850.IedConnection_readTimestampValue(self.__con, var, self.get_IEC61850_FC_by_fc(fc), time)
        return iec61850.Timestamp_getTimeInMs(time)

    def getInt32(self, var):
        [intValue, self.__error] = iec61850.IedConnection_readFloatValue(self.__con, var, iec61850.IEC61850_FC_MX)
        return intValue

    def read_quality(self, var, fc):
        [qualityValue, self.__error] = iec61850.IedConnection_readQualityValue(self.__con, var, self.get_IEC61850_FC_by_fc(fc))
        return qualityValue

    def stop(self):
        iec61850.IedConnection_close(self.__con)
        iec61850.IedConnection_destroy(self.__con)
        #sys.exit()

    def get_rcb(self, CBref):
        [self.__rcb, self._error] = iec61850.IedConnection_getRCBValues(self.__con, CBref, None)
        if (self._error == iec61850.IED_ERROR_OK):
            print("RCB read success")
        else:
            print("failed to read RCB")

    def get_rcb_dictionary(self, report_name):
        [self.__rcb, error] = iec61850.IedConnection_getRCBValues(self.__con, report_name, None)
        if (error == iec61850.IED_ERROR_OK):
            rcb_dict = {}
            rcb_dict['buffered'] = iec61850.ClientReportControlBlock_isBuffered(self.__rcb)
            rcb_dict['bufTime'] = str(iec61850.ClientReportControlBlock_getBufTm(self.__rcb))
            rcb_dict['confRev'] = str(iec61850.ClientReportControlBlock_getConfRev(self.__rcb))
            rcb_dict['datSet'] = iec61850.ClientReportControlBlock_getDataSetReference(self.__rcb)
            rcb_dict['CBref'] = iec61850.ClientReportControlBlock_getObjectReference(self.__rcb)
            rcb_dict['rptID'] = iec61850.ClientReportControlBlock_getRptId(self.__rcb)
            rcb_dict['trgOpt'] = format(iec61850.ClientReportControlBlock_getTrgOps(self.__rcb), '04b')
            rcb_dict['OptFields'] = format(iec61850.ClientReportControlBlock_getOptFlds(self.__rcb), '05b')
            rcb_dict['dchg'] = bool(rcb_dict['trgOpt'][-1] == '1')
            rcb_dict['qchg'] = bool(rcb_dict['trgOpt'][-2]== '1')
            rcb_dict['dupd'] = bool(rcb_dict['trgOpt'][-3] == '1')
            rcb_dict['period'] = bool(rcb_dict['trgOpt'][-4] == '1')
            rcb_dict['seqNum'] = bool(rcb_dict['OptFields'][-1] == '1')
            rcb_dict['timeStamp'] = bool(rcb_dict['OptFields'][-2] == '1')
            rcb_dict['reasonCode'] = bool(rcb_dict['OptFields'][-3] == '1')
            rcb_dict['dataSet'] = bool(rcb_dict['OptFields'][-4]== '1')
            rcb_dict['dataRef'] = bool(rcb_dict['OptFields'][-5]== '1')
            return rcb_dict
        else:
            print("failed to read RCB")
            self.stop()

    def getDataSetDirectory(self):
        isDel = None
        #Working with Reports:
        [self.dataset_dir, self.__error] = iec61850.IedConnection_getDataSetDirectory(self.__con, "RP2_19LD0/LLN0.MxDs", isDel)
        if (self.__error == iec61850.IED_ERROR_OK):
            print("OK")
            if isDel:
                print("Dataset: (deletable)")
            else:
                print("Dataset: (not deletable)")
        else:
            print ("Connection error status")
            self.stop()

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

    def func_handler(self, param, ptr):
        print("------------ Func Handler")
        print("Size of Directory", iec61850.LinkedList_size(self.dataset_dir))
        ds_size = iec61850.LinkedList_size(self.dataset_dir)
        report = iec61850.ClientReport_FromInt(ptr)
        for i in range(ds_size):
            reas = iec61850.ClientReport_getReasonForInclusion(report, i)
            print("Reason of entry: ", i, iec61850.ReasonForInclusion_getValueAsString(reas))
        mmsvalue = iec61850.ClientReport_getDataSetValues(report)
        array_size = iec61850.MmsValue_getArraySize(mmsvalue)
        element1 = iec61850.MmsValue_getElement(mmsvalue, 1)
        print('Element 1 = :', iec61850.MmsValue_getTypeString(element1))
        print('Array Size :', array_size)
        print('To String', iec61850.MmsValue_toString(mmsvalue))
        print('Is Deletable',iec61850.MmsValue_isDeletable(mmsvalue))
        print('To Float', iec61850.MmsValue_toFloat(element1))
        type_string = iec61850.MmsValue_getTypeString(mmsvalue)
        print('String Type:', type_string)
        quality = iec61850.Quality_fromMmsValue(mmsvalue)
        print('Quality:', quality)
        # iec61850.MmsValue_delete(mmsvalue)
        print("Got report: " + str(iec61850.ClientReport_getRcbReference(report)))
        ds_name = iec61850.ClientReport_getDataSetName(report)
        print('Dataset name:',ds_name)
        rcb_ref = iec61850.ClientReport_getRcbReference(report)
        print('RCB reference', rcb_ref)
        report_id = iec61850.ClientReport_getRptId(report)
        print('Report ID', report_id)
        reason = iec61850.ClientReport_getReasonForInclusion(report, 1)
        print('Reason', reason)
        entry_id = iec61850.ClientReport_getEntryId(report)
        print('Entry ID', entry_id)
        has_timestamp = iec61850.ClientReport_hasTimestamp(report)
        print('has timestamp', has_timestamp)
        has_seq_num = iec61850.ClientReport_hasSeqNum(report)
        print('has seq number', has_seq_num)
        seq_num = iec61850.ClientReport_getSeqNum(report)
        print('Seq number', seq_num)
        has_dataset_name = iec61850.ClientReport_hasDataSetName(report)
        print('has dataset name', has_dataset_name)
        has_reason = iec61850.ClientReport_hasReasonForInclusion(report)
        print('has reason', has_reason)
        has_conf_rev = iec61850.ClientReport_hasConfRev(report)
        print('has conf rev', has_conf_rev)
        conf_rev = iec61850.ClientReport_getConfRev(report)
        print('conf rev', conf_rev)
        has_buf_ovfl = iec61850.ClientReport_hasBufOvfl(report)
        print('has overflow buffer', has_buf_ovfl)
        buf_ovfl = iec61850.ClientReport_getBufOvfl(report)
        print('Buffer overflow', buf_ovfl)
        has_dataset_ref = iec61850.ClientReport_hasDataReference(report)
        print('has dataset ref', has_dataset_ref)
        dataset_ref = iec61850.ClientReport_getDataReference(report, 0)
        print('dataset ref', dataset_ref)
        time_stamp = iec61850.ClientReport_getTimestamp(report)
        print('time_stamp', time_stamp)
        reason_string = iec61850.ReasonForInclusion_getValueAsString(reason)
        print('Reason string', reason_string)
        print("*"*50)
        print("Report received!")

    def install_handler1(self):
        print("Start")
        hostname = "localhost"
        tcpPort = 102
        con = iec61850.IedConnection_create()
        error = iec61850.IedConnection_connect(con, hostname, tcpPort)
        print(str(error))
        CB_PROTO = CFUNCTYPE(None, c_void_p, c_void_p)
        cbinst = CB_PROTO(self.func_handler)
        val = c_int()
        api = CDLL("/home/ivan/Projects/libiec61850/build/src/libiec61850.so")
        ReportHandler = api.IedConnection_installReportHandlerAddr
        ReportHandler.argtypes = [c_uint, c_char_p, c_char_p, CB_PROTO, c_void_p]
        ReportHandler.restype = None
        addr=iec61850.IedConnection_ToAddress(con)
        rcb, error = iec61850.IedConnection_getRCBValues(con,"TEMPLATELD0/LLN0.BR.brcbST0101", None)
        print("RCB:" + str(rcb))
        rid = iec61850.ClientReportControlBlock_getRptId(rcb)
        print("OriginalID: " + rid)
        rptRef = create_string_buffer(b"TEMPLATELD0/LLN0.BR.brcbST0101")
        rptID = create_string_buffer(b"TEMPLATELD0/LLN0$BR$brcbST0101")
        ReportHandler(addr, rptRef,rptID, cbinst, None)
        print("Enabled " + str(iec61850.ClientReportControlBlock_getRptEna(rcb)))
        iec61850.ClientReportControlBlock_setTrgOps(rcb, iec61850.TRG_OPT_DATA_UPDATE | iec61850.TRG_OPT_GI);
        iec61850.ClientReportControlBlock_setRptEna(rcb, True)
        error = iec61850.IedConnection_setRCBValues(con, rcb, iec61850.RCB_ELEMENT_RPT_ENA | iec61850.RCB_ELEMENT_TRG_OPS, True)
        print(error)
        if (error == iec61850.IED_ERROR_OK):
            print("Connection is OK")
        else:
            print ("Connection error status")
        print("Enabled " + str(iec61850.ClientReportControlBlock_getRptEna(rcb)))
        input("Wait input ... ")
        iec61850.IedConnection_close(con)
        iec61850.IedConnection_destroy(con)

    def install_handler0(self):
        CB_PROTO = CFUNCTYPE(None, c_void_p, c_void_p)
        cbinst = CB_PROTO(self.func_handler)
        val = c_int()
        api = CDLL("/home/ivan/Projects/libiec61850/build/src/libiec61850.so")
        ReportHandler = api.IedConnection_installReportHandlerAddr
        ReportHandler.argtypes = [c_uint, c_char_p, c_char_p, CB_PROTO, c_void_p]
        ReportHandler.restype = None
        addr=iec61850.IedConnection_ToAddress(self.__con)
        self.__rcb, self.__error = iec61850.IedConnection_getRCBValues(self.__con,"RP2_19LD0/LLN0.BR.brcbMX01", None)
        iec61850.ClientReportControlBlock_setRptEna(self.__rcb, True)
        iec61850.ClientReportControlBlock_setTrgOps(self.__rcb, iec61850.TRG_OPT_DATA_CHANGED | iec61850.TRG_OPT_QUALITY_CHANGED)
        print(iec61850.ClientReportControlBlock_getRptId(self.__rcb))
        rptRef = create_string_buffer(bytes("RP2_19LD0/LLN0.BR.brcbMX01", encoding='UTF-8'))
        # rptID = create_string_buffer(bytes("RP2_19LD0/LLN0$BR$brcbMX01", encoding='UTF-8'))
        rptID = create_string_buffer(bytes(iec61850.ClientReportControlBlock_getRptId(self.__rcb), encoding='UTF-8'))
        ReportHandler(addr, rptRef,rptID, cbinst, None)
        error = iec61850.IedConnection_setRCBValues(self.__con,self.__rcb, iec61850.RCB_ELEMENT_RPT_ENA | iec61850.RCB_ELEMENT_TRG_OPS  , True)
        input("Wait input ... ")

    def install_handler_from_c(self):
        print("Start")
        hostname = "localhost"
        tcpPort = 102
        con = iec61850.IedConnection_create()
        error = iec61850.IedConnection_connect(con, hostname, tcpPort)

        CB_PROTO = CFUNCTYPE(None, c_void_p, c_void_p)
        cbinst = CB_PROTO(self.func_handler)
        val = c_int()
        api = CDLL("/home/ivan/Projects/libiec61850/build/src/libiec61850.so")
        ReportHandler = api.IedConnection_installReportHandlerAddr
        ReportHandler.argtypes = [c_uint, c_char_p, c_char_p, CB_PROTO, c_void_p]
        ReportHandler.restype = None
        addr=iec61850.IedConnection_ToAddress(con)

        rcb, error = iec61850.IedConnection_getRCBValues(con,"RP2_19LD0/LLN0.BR.brcbMX01", None)
        # iec61850.ClientReportControlBlock_setDataSetReference(rcb, "RP2_19LD0/LLN0$MxDs")
        iec61850.ClientReportControlBlock_setRptEna(rcb, True)
        # iec61850.ClientReportControlBlock_setGI(rcb, True)
        iec61850.ClientReportControlBlock_setTrgOps(rcb, iec61850.TRG_OPT_DATA_CHANGED | iec61850.TRG_OPT_QUALITY_CHANGED)
        print(iec61850.ClientReportControlBlock_getRptId(rcb))
        rptRef = create_string_buffer(bytes("RP2_19LD0/LLN0.BR.brcbMX01", encoding='UTF-8'))
        rptID = create_string_buffer(bytes(iec61850.ClientReportControlBlock_getRptId(rcb), encoding='UTF-8'))
        ReportHandler(addr, rptRef,rptID, cbinst, None)
        error = iec61850.IedConnection_setRCBValues(con, rcb, iec61850.RCB_ELEMENT_RPT_ENA | iec61850.RCB_ELEMENT_TRG_OPS  , True)
        input("Wait input ... ")
        iec61850.IedConnection_close(con)
        iec61850.IedConnection_destroy(con)

    def install_handler2(self, CBref, rID):
        CB_PROTO = CFUNCTYPE(None, c_void_p, c_void_p)
        cbinst = CB_PROTO(self.func_handler)
        api = CDLL("/home/ivan/Projects/libiec61850/debug/src/libiec61850.so")
        ReportHandler = api.IedConnection_installReportHandlerAddr
        ReportHandler.argtypes = [c_uint, c_char_p, c_char_p, CB_PROTO, c_void_p]
        ReportHandler.restype = None
        addr = iec61850.IedConnection_ToAddress(self.__con)
        # self.__rcb, self.__error = iec61850.IedConnection_getRCBValues(self.__con, CBref, None)
        print("RCB:" + str(self.__rcb))
        rid = iec61850.ClientReportControlBlock_getRptId(self.__rcb)
        print("OriginalID: " + rid)
        rptRef = create_string_buffer(bytes(CBref, encoding='UTF-8'))
        rptID = create_string_buffer(bytes(rID, encoding='UTF-8'))
        # rptRef = create_string_buffer(b"TEMPLATELD0/LLN0.BR.brcbST0101")
        # rptID = create_string_buffer(b"TEMPLATELD0/LLN0$BR$brcbST0101")
        ReportHandler(addr, rptRef, rptID, cbinst, None)
        # iec61850.ClientReportControlBlock_setTrgOps(self.__rcb, iec61850.TRG_OPT_DATA_CHANGED | iec61850.TRG_OPT_QUALITY_CHANGED | iec61850.TRG_OPT_INTEGRITY | iec61850.TRG_OPT_GI)
        # iec61850.ClientReportControlBlock_setRptEna(self.__rcb, True)
        # self.__error = iec61850.IedConnection_setRCBValues(self.__con, self.__rcb, iec61850.RCB_ELEMENT_RPT_ENA | iec61850.RCB_ELEMENT_TRG_OPS, True)
        # print("Enabled " + str(iec61850.ClientReportControlBlock_getRptEna(self.__rcb)))
        input("Wait input....")

    def install_handler(self, CBref):
        CB_PROTO = CFUNCTYPE(None, c_void_p, c_void_p)
        cbinst = CB_PROTO(self.func_handler)
        api = CDLL("/home/ivan/Projects/libiec61850/debug/src/libiec61850.so")
        ReportHandler = api.IedConnection_installReportHandlerAddr
        ReportHandler.argtypes = [c_uint, c_char_p, c_char_p, CB_PROTO, c_void_p]
        ReportHandler.restype = None
        addr = iec61850.IedConnection_ToAddress(self.__con)
        iec61850.ClientReportControlBlock_setRptEna(self.__rcb, True)
        iec61850.ClientReportControlBlock_setTrgOps(self.__rcb, iec61850.TRG_OPT_DATA_CHANGED | iec61850.TRG_OPT_QUALITY_CHANGED | iec61850.TRG_OPT_INTEGRITY | iec61850.TRG_OPT_GI)
        rid = iec61850.ClientReportControlBlock_getRptId(self.__rcb)
        rptRef = create_string_buffer(bytes(CBref, encoding='UTF-8'))
        rptID = create_string_buffer(bytes(rid, encoding='UTF-8'))
        ReportHandler(addr, rptRef, rptID, cbinst, None)
        self.__error = iec61850.IedConnection_setRCBValues(self.__con, self.__rcb, iec61850.RCB_ELEMENT_RPT_ENA | iec61850.RCB_ELEMENT_TRG_OPS, True)
        input("Wait input....")

    def triggerReport(self):
        iec61850.IedConnection_triggerGIReport(self.__con, "TEMPLATELD0/LLN0.BR.brcbMX0201")

    def trigger_gi(self, CBref):
        iec61850.IedConnection_triggerGIReport(self.__con, CBref)

    def get_report_enabled(self):
        print("Is Enabled: " + str(iec61850.ClientReportControlBlock_getRptEna(self.__rcb)))

    def enable_report(self):
        print("Enabling rptEna")
        iec61850.ClientReportControlBlock_setRptEna(self.__rcb, True)
        self.__error = iec61850.IedConnection_setRCBValues(self.__con, self.__rcb, iec61850.RCB_ELEMENT_RPT_ENA, True)

    def disable_report(self):
        print("Disabling report")
        iec61850.ClientReportControlBlock_setRptEna(self.__rcb, False)

    def destroy_report(self):
        print("Destroying report ...")
        iec61850.ClientReportControlBlock_destroy(self.__rcb)

    def disableReport(self):
        print("disable rptEna")
        iec61850.ClientReportControlBlock_setResv(self.__rcb, False)
        iec61850.ClientReportControlBlock_setRptEna(self.__rcb, False)
        iec61850.ClientReportControlBlock_setGI(self.__rcb, False)
        iec61850.IedConnection_setRCBValues(self.__con, self.__rcb, iec61850.RCB_ELEMENT_GI, False)

    def read_object(self, varname, fc):
        [obj, self._error] = iec61850.IedConnection_readObject(self.__con, varname, self.get_IEC61850_FC_by_fc(fc))
        objtype = iec61850.MmsValue_getTypeString(obj)
        iec61850.MmsValue_delete(obj)
        return objtype

    def read_object_test(self):
        [stVal, error] = iec61850.IedConnection_readObject(self.__con, "ECISepam80_8/CSWI1.Loc.stVal", iec61850.IEC61850_FC_ST)
        [hz, error] = iec61850.IedConnection_readObject(self.__con, "ECISepam80_8/MMXU1.Hz.mag", iec61850.IEC61850_FC_MX)
        [quality, error] = iec61850.IedConnection_readObject(self.__con, "ECISepam80_8/MMXU1.Hz.q", iec61850.IEC61850_FC_MX)
        [timeStampValue, error] = iec61850.IedConnection_readObject(self.__con, "ECISepam80_8/MMXU1.Hz.t", iec61850.IEC61850_FC_MX)
        [db, error] = iec61850.IedConnection_readObject(self.__con, "ECISepam80_8/MMXU1.Hz.db", iec61850.IEC61850_FC_CF)
        state = iec61850.MmsValue_getBoolean(stVal)
        type_string = iec61850.MmsValue_getTypeString(stVal)
        hz_type = iec61850.MmsValue_getTypeString(hz)
        quality_type = iec61850.MmsValue_getTypeString(quality)
        time_type = iec61850.MmsValue_getTypeString(timeStampValue)
        db_type = iec61850.MmsValue_getTypeString(db)
        iec61850.MmsValue_delete(stVal)
        print("StVal:\t\t", state)
        print("TypeStval:\t", type_string)
        print("MagVal_Type:\t\t", hz_type)
        print("Quality_Type:\t\t", quality_type)
        print("TimeStamp_Type:\t\t", time_type)
        print("DB_Type:\t\t", db_type)
        # =============================
        [mag, error] = iec61850.IedConnection_readObject(self.__con, "ECISepam20_7/MSTA1.TrAmp3.mag", iec61850.IEC61850_FC_MX)
        print("Mag_Type:\t\t", iec61850.MmsValue_getTypeString(mag))
        [f, error] = iec61850.IedConnection_readObject(self.__con, "ECISepam20_7/MSTA1.TrAmp3.mag.f", iec61850.IEC61850_FC_MX)
        print("F_Type:\t\t\t", iec61850.MmsValue_getTypeString(f))
        [q, error] = iec61850.IedConnection_readObject(self.__con, "ECISepam20_7/MSTA1.TrAmp3.q", iec61850.IEC61850_FC_MX)
        print("q_Type:\t\t\t", iec61850.MmsValue_getTypeString(q))
        [Timestamp, error] = iec61850.IedConnection_readObject(self.__con, "ECISepam20_7/MSTA1.TrAmp3.t", iec61850.IEC61850_FC_MX)
        print("F_Type:\t\t\t", iec61850.MmsValue_getTypeString(Timestamp))
        [db, error] = iec61850.IedConnection_readObject(self.__con, "ECISepam20_7/MSTA1.TrAmp3.db", iec61850.IEC61850_FC_CF)
        print("db_Type:\t\t", iec61850.MmsValue_getTypeString(db))
        [dataNs, error] = iec61850.IedConnection_readObject(self.__con, "ECISepam20_7/MSTA1.TrAmp3", iec61850.IEC61850_FC_EX)
        print("dataNs_Type:\t\t", iec61850.MmsValue_getTypeString(dataNs))
        [enum, error] = iec61850.IedConnection_readObject(self.__con, "ECISepam20_7/A49_PTTR1.Mod.stVal", iec61850.IEC61850_FC_ST)
        print("enum Type:\t\t", iec61850.MmsValue_getTypeString(enum))
        [string, error] = iec61850.IedConnection_readObject(self.__con, "ECISepam20_7/A49T_PTTR6.NamPlt.d", iec61850.IEC61850_FC_DC)
        print("string Type:\t\t", iec61850.MmsValue_getTypeString(string))
        [float_var, error] = iec61850.IedConnection_readObject(self.__con, "ECISepam20_7/A49T_PTTR8.Tmp.mag.f", iec61850.IEC61850_FC_MX)
        print("float Type:\t\t", iec61850.MmsValue_getTypeString(float_var))
        [int_var, error] = iec61850.IedConnection_readObject(self.__con, "ECISepam20_7/XCBR1.ChaTms.stVal", iec61850.IEC61850_FC_ST)
        print("int signed Type:\t\t", iec61850.MmsValue_getTypeString(int_var))
        [uint_var, error] = iec61850.IedConnection_readObject(self.__con, "ECISepam20_7/A49T_PTTR7.Tmp.db", iec61850.IEC61850_FC_CF)
        print("Usigned Type:\t\t", iec61850.MmsValue_getTypeString(uint_var))
        [octet, error] = iec61850.IedConnection_readObject(self.__con, "ECISepam40_5/RREC1.BlkRec.Oper.origin.orIdent", iec61850.IEC61850_FC_CO)
        print("octet Type:\t\t", iec61850.MmsValue_getTypeString(octet))
        [check, error] = iec61850.IedConnection_readObject(self.__con, "ECISepam80_8/A49_PTTR1.InhThmPro.Oper.Check", iec61850.IEC61850_FC_CO)
        print("check Type:\t\t", iec61850.MmsValue_getTypeString(check))
        [dbPos, error] = iec61850.IedConnection_readObject(self.__con, "ECISepam80_8/XCBR1.Pos.stVal", iec61850.IEC61850_FC_ST)
        print("dbPos Type:\t\t", iec61850.MmsValue_getTypeString(dbPos))
        [int128, error] = iec61850.IedConnection_readObject(self.__con, "ECISepam80_8/XCBR1.SumSwARs.actVal", iec61850.IEC61850_FC_ST)
        print("int128 Type:\t\t", iec61850.MmsValue_getTypeString(int128))

    def read_time_test(self):
        time = iec61850.Timestamp()
        [timeStampValue, self.__error] = iec61850.IedConnection_readTimestampValue(self.__con, "ECISepam80_8/A51N_PTOC6.Op.t", iec61850.IEC61850_FC_MX, time)
        return iec61850.Timestamp_getTimeInMs(time)

    def read_float_test(self):
        float_value = self.read_float("TEMPLATELD0/MMXU3.PhV.phsA.cVal.mag.f", 'MX')
        print(float_value)

    def read_boolean_test(self):
        val = self.read_boolean("TEMPLATELD0/PTRC1.BlkInd1.stVal")
        print(val)

    def get_fc_by_varname(self, varname):
        [deviceList, self.__error] = iec61850.IedConnection_getLogicalDeviceList(self.__con)
        device = iec61850.LinkedList_getNext(deviceList)
        while device:
            ld_inst = iec61850.toCharP(device.data)
            [logicalNodes, self.__error] = iec61850.IedConnection_getLogicalDeviceDirectory(self.__con, iec61850.toCharP(device.data))
            lnode = iec61850.LinkedList_getNext(logicalNodes)
            while lnode:
                ln_name = iec61850.toCharP(lnode.data)
                [variables, self.__error] = iec61850.IedConnection_getLogicalNodeVariables(self.__con, ld_inst+'/'+ln_name)
                variable = iec61850.LinkedList_get(variables, 0)
                vIndex = 1
                while variable:
                    name = iec61850.toCharP(variable.data)
                    #fc_name = name.split("$", 1)[0]
                    if '$' in name:
                        var_name = name.split("$",1)[1]
                        var_name = var_name.replace("$", ".")
                        #print(fc_name, "-----FC------>" , vIndex)
                        #var_dict[ld_inst+'/'+ln_name+'.'+var_name]=fc_name
                        temp_name = ld_inst+'/'+ln_name+'.'+var_name
                        if varname == temp_name:
                            fc_name = name.split("$", 1)[0]
                    variable = iec61850.LinkedList_get(variables, vIndex)
                    vIndex += 1
                iec61850.LinkedList_destroy(variables)
                lnode = iec61850.LinkedList_getNext(lnode)
            iec61850.LinkedList_destroy(logicalNodes)
            device = iec61850.LinkedList_getNext(device)
        iec61850.LinkedList_destroy(deviceList)
        return fc_name

    def read_quality_test(self, var_name):
        [qualityValue, self.__error] = iec61850.IedConnection_readQualityValue(self.__con, var_name, iec61850.IEC61850_FC_ST)
        print(qualityValue)

    def read_uint32_test(self, var_name):
        [intValue, self.__error] = iec61850.IedConnection_readUnsigned32Value(self.__con, var_name, iec61850.IEC61850_FC_ST)
        print(intValue)

    def read_int32_test(self, var_name):
        [intValue, self.__error] = iec61850.IedConnection_readInt32Value(self.__con, var_name, iec61850.IEC61850_FC_ST)
        print(int(intValue))

    def read_st_test(self, var):
        [stValue, self.__error] = iec61850.IedConnection_readUnsigned32Value(self.__con, var, iec61850.IEC61850_FC_ST)
        print('stVal Value:\t\t', stValue)
        [st, self.__error] = iec61850.IedConnection_readObject(self.__con, var, iec61850.IEC61850_FC_ST)
        print("STVal_Type:\t\t", iec61850.MmsValue_getBitStringSize(st))
        print("STVal_Type:\t\t", iec61850.MmsValue_getBitStringAsInteger(st))
        iec61850.MmsValue_delete(st)

    def get_vartype(self, var):
        return self.get_vartype_by_fc(var, self.get_fc_by_varname(var))

    def read_var(self, var):
        var_type = self.get_vartype_by_fc(var, self.get_fc_by_varname(var))
        fc = self.get_IEC61850_FC_by_fc(self.get_fc_by_varname(var))
        [mms_object, self.__error] = iec61850.IedConnection_readObject(self.__con, var, fc)
        mms_value = 0
        if var_type == 'bit-string':
            mms_value = iec61850.MmsValue_getBitStringAsInteger(mms_object)
        if var_type == 'utc-time':
            mms_value = iec61850.MmsValue_getUtcTimeInMs(mms_object)
        if var_type == 'integer':
            mms_value = iec61850.MmsValue_toInt64(mms_object)
        if var_type == 'boolean':
            mms_value = str(iec61850.MmsValue_getBoolean(mms_object))
        if var_type == 'unsigned':
            mms_value = iec61850.MmsValue_toUint32(mms_object)
        if var_type == 'float':
            mms_value = float("{0:.3f}".format(iec61850.MmsValue_toFloat(mms_object)))
        if var_type == 'octet-string':
            mms_value = iec61850.MmsValue_getOctetStringSize(mms_object)
        if var_type not in ['bit-string', 'unsigned','utc-time', 'integer', 'boolean', 'float', 'octet-string']:
            print(var_type)
        iec61850.MmsValue_delete(mms_object)
        return mms_value, var_type

if __name__ == "__main__":
    try:
        clt=IecClient()
        cltThread = threading.Thread(target = clt.run)
        cltThread.start()
        #clt.get_model_from_server()
        # for ld in clt.get_ld_list():
        #     print("Checkin===",clt.get_name_of(ld))
        #     print("##########")
        #     for rc in clt.get_rcbr_list_by_ldname(clt.get_name_of(ld)):
        #         print("Working with RC buffered ---- > ", rc)
        #     for rp in clt.get_rcrp_list_by_ldname(clt.get_name_of(ld)):
        #         print("Working with RC Unbuffered ---- > ", rp)
        #print(clt.get_rcb_dictionary('TEMPLATELD0/LLN0.BR.brcbST0101'))
        #print(clt.read_time_test())

        #clt.readInt32('ECISepam20_7/MSTA1.TrAmp3.mag.f')
        #clt.readST('ECISepam40_1/XCBR1.CBOpCap.stVal')
        #print(clt.get_varlist_by_ld_lnname('ECISepam20_7/MSTA1'))
        clt.stop()
    except:
        running = 0
        print ("Error :")
        traceback.print_exc(file=sys.stdout)
        sys.exit(-1)
