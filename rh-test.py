import os,sys
import iec61850
from ctypes import *

def test_func(param,ptr):
    print("Handler")
    print(type(ptr))
    print(ptr)
    print(type(param))
    report = iec61850.ClientReport_FromInt(ptr)
    mmsvalue = iec61850.ClientReport_getDataSetValues(report)
    print("Got report: " + str(iec61850.ClientReport_getRcbReference(report)))


if __name__=="__main__":
    print("Start")
    hostname="localhost"
    tcpPort=102
    con = iec61850.IedConnection_create()
    error = iec61850.IedConnection_connect(con, hostname, tcpPort)
    print(str(error))
    CB_PROTO=CFUNCTYPE(None, c_void_p, c_void_p)
    cbinst=CB_PROTO(test_func)
    val = c_int()
    #iec61850.IedConnection_installReportHandler(con,"111","111",cbinst, ctypes.byref(val))
    api=CDLL("/home/ivan/Projects/libiec61850/build/src/libiec61850.so")
    #api=CDLL("/home/alexs/projects/libiec-dirty/debug/src/libiec61850-drt.so")
    ReportHandler=api.IedConnection_installReportHandlerAddr

    ReportHandler.argtypes=[c_uint, c_char_p, c_char_p, CB_PROTO, c_void_p]
    ReportHandler.restype = None

    addr=iec61850.IedConnection_ToAddress(con)

    rcb, error = iec61850.IedConnection_getRCBValues(con,"TEMPLATELD0/LLN0.BR.brcbMX0101", None)

    print("RCB:" + str(rcb))
    rid = iec61850.ClientReportControlBlock_getRptId(rcb)
    print("OriginalID: " + rid)

    rptRef=create_string_buffer(b"TEMPLATELD0/LLN0.BR.brcbMX0101")
    rptID = create_string_buffer(b"TEMPLATELD0/LLN0$BR$brcbMX0101")
    ReportHandler(addr, rptRef,rptID, cbinst, None)

    print("Enabled: " + str(iec61850.ClientReportControlBlock_getRptEna(rcb)))


    iec61850.ClientReportControlBlock_setTrgOps(rcb, iec61850.TRG_OPT_DATA_UPDATE | iec61850.TRG_OPT_GI);
    iec61850.ClientReportControlBlock_setRptEna(rcb,True)
    error = iec61850.IedConnection_setRCBValues(con, rcb, iec61850.RCB_ELEMENT_RPT_ENA | iec61850.RCB_ELEMENT_TRG_OPS, True)

    print(error)
    input("Wait input....")
    iec61850.IedConnection_close(con)
    iec61850.IedConnection_destroy(con)
