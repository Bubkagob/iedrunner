import sys
import threading
import traceback
import getch
import iec61850


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
                print("ошибка",self.__error)
        except Exception as e:
            print('Connection exception: ', str(e))
            running = 0
            #sys.exit(-1)

    def get_connection_state(self):
        return iec61850.IedConnection_getState(self.__con)

    def get_ied_ld_names(self):
        iednames = []
        [deviceList, error] = iec61850.IedConnection_getLogicalDeviceList(self.__con)
        device = iec61850.LinkedList_getNext(deviceList)
        while device: #Iterate over each device from deviceList
            iednames.append(iec61850.toCharP(device.data))
            device = iec61850.LinkedList_getNext(device)
        iec61850.LinkedList_destroy(deviceList)
        return iednames

    def get_name_of(self, obj):
        return iec61850.toCharP(obj.data)

    def get_model_from_server(self):
        model = iec61850.IedConnection_getDeviceModelFromServer(self.__con)

    def get_ld_list(self):
        ld_list = []
        [ldList, self.__error] = iec61850.IedConnection_getLogicalDeviceList(self.__con)
        device = iec61850.LinkedList_getNext(ldList)
        while device: #Iterate over each device from deviceList
            ld_list.append(device)
            device = iec61850.LinkedList_getNext(device)
        #iec61850.LinkedList_destroy(ldList)
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

    def readBoolean(self, var):
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
        [self.__rcb, error] = iec61850.IedConnection_getRCBValues(self.__con, "ECISepam80_8/LLN0.BR.brcbMX01", None)
        if (error == iec61850.IED_ERROR_OK):
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
        [self.__dataSetDirectory, error] = iec61850.IedConnection_getDataSetDirectory(self.__con, "ECISepam80_8/LLN0.MxDs", isDel)
        if (error == iec61850.IED_ERROR_OK):
            print("OK")
            if isDel:
                print("Dataset: (deletable)")
            else:
                print("Dataset: (not deletable)")
        else:
            print ("Connection error status")
            self.stop()
            #sys.exit(-1)

    def installHandler(self):
        print("--------------------Install Report receiver")
        iec61850.IedConnection_installReportHandler(self.__con,
                                                    "ECISepam80_8/LLN0.BR.brcbMX0101",
                                                    iec61850.ClientReportControlBlock_getRptId(self.__rcb),
                                                    self.reportCallbackFunction,
                                                    self.__dataSetDirectory
                                                    )

    def triggerReport(self):
        iec61850.IedConnection_triggerGIReport(self.__con, "ECISepam80_8/LLN0.BR.brcbMX0101")

    def enableReport(self):
        print("Enabling rptEna")
        iec61850.ClientReportControlBlock_setResv(self.__rcb, True)
        iec61850.ClientReportControlBlock_setDataSetReference(self.__rcb, "ECISepam80_8/LLN0$MxDs")
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

    def read_quality_test(self):
        [qualityValue, self.__error] = iec61850.IedConnection_readQualityValue(self.__con, "ECISepam20_7/MSTA1.TrAmp3.q", iec61850.IEC61850_FC_MX)
        print(qualityValue)

    def read_time_test(self):
        time = iec61850.Timestamp()
        [timeStampValue, self.__error] = iec61850.IedConnection_readTimestampValue(self.__con, "ECISepam80_8/A51N_PTOC6.Op.t", iec61850.IEC61850_FC_MX, time)
        return iec61850.Timestamp_getTimeInMs(time)


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
        #print(clt.get_rcb_dictionary('ECISepam20_7/LLN0.BR.brcbMX01'))
        #print(clt.read_time_test())

        #clt.readInt32('ECISepam20_7/MSTA1.TrAmp3.mag.f')
        #clt.readST('ECISepam40_1/XCBR1.CBOpCap.stVal')
        #print(clt.get_varlist_by_ld_lnname('ECISepam20_7/MSTA1'))
        #clt.stop()
    except:
        running = 0
        print ("Error :")
        traceback.print_exc(file=sys.stdout)
        sys.exit(-1)
