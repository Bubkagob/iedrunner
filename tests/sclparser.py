from lxml import etree, objectify

def getRoot(scd):
    root = objectify.parse(scd)
    SCL = root.getroot()
    return SCL


def getSubnetwork_list(root):
    sn_list = []
    for sn in root.Communication.iterchildren():
        sn_list.append(sn)
    return sn_list

def getConnectedAP_list(subnetwork_list):
    ap_list = []
    for sn in subnetwork_list:
        for capp in sn.iterchildren():
            ap_list.append(capp)
    return ap_list


def get_ip_list(scd):
    ip_list = []
    for ap in getConnectedAP_list(getSubnetwork_list(getRoot(scd))):
        for address in ap.Address.iterchildren():
            if address.get('type') == 'IP':
                ip_list.append(address)
    return ip_list


def getIEDnameByIp(scd, ip):
    for ap in getConnectedAP_list(getSubnetwork_list(getRoot(scd))):
        for address in ap.Address.iterchildren():
            if address.get('type') == 'IP' and address == ip:
                return ap.get('iedName')


def getIEDlist(root):
    res_list=[]
    for ied in root.IED:
        res_list.append(ied)
    return res_list


def getIEDbyIp(scd, ip):
    ied_list=[]
    for ied in getIEDlist(getRoot(scd)):
        if ied.get('name') == getIEDnameByIp(scd, ip):
            ied_list.append(ied)
    return ied_list


def getLNlist(ied):
    ln_list=[]
    for i in ied:
        for element in i.AccessPoint.Server.LDevice.iter():
            if 'lnClass' and 'lnType' in element.attrib:
                ln_list.append(element)
        return ln_list


def get_Pretty_LNlist(lnode):
    if 'prefix' in lnode.attrib:
        if(lnode.get('prefix')):
            return (lnode.get('prefix')+lnode.get('lnClass')+lnode.get('inst'))
        else:
            return (lnode.get('lnClass')+lnode.get('inst'))
    else:
        return lnode.get('lnClass')

def getDataSetList(lnodelist):
    ds_list=[]
    for lnode in lnodelist:
        for ds in lnode.iterchildren(tag='{http://www.iec.ch/61850/2003/SCL}DataSet'):
            ds_list.append(ds)
    return ds_list

def getReportList(lnodelist):
    reports=[]
    for lnode in lnodelist:
        for report in lnode.iterchildren(tag='{http://www.iec.ch/61850/2003/SCL}ReportControl'):
            reports.append(report)
    return reports

def getDOlist(lnodelist):
    do_list=[]
    for lnode in lnodelist:
        for do in lnode.DOI:
            do_list.append(do)
    return do_list

def getLNodeTypes(root):
    res_list=[]
    ddt = root.find('{http://www.iec.ch/61850/2003/SCL}DataTypeTemplates')
    for lntype in ddt.LNodeType:
        res_list.append(lntype)
    return res_list

def getDOTypes(root):
    res_list=[]
    ddt = root.find('{http://www.iec.ch/61850/2003/SCL}DataTypeTemplates')
    for dotype in ddt.DOType:
        res_list.append(dotype)
    return res_list

def getDATypes(root):
    res_list=[]
    ddt = root.find('{http://www.iec.ch/61850/2003/SCL}DataTypeTemplates')
    for datype in ddt.DAType:
        res_list.append(datype)
    return res_list

def getEnumTypes(root):
    res_list=[]
    ddt = root.find('{http://www.iec.ch/61850/2003/SCL}DataTypeTemplates')
    for etype in ddt.EnumType:
        res_list.append(etype)
    return res_list








'''
#############################################################################
'''
def LNTypes(scd):
    root = objectify.parse(scd)
    LNDataList = []
    for ied in root.findall('{http://www.iec.ch/61850/2003/SCL}DataTypeTemplates'):
         for ln in ied.LNodeType:
             if ln.attrib.get('id'):
                 LNDataList.append(ln.attrib.get('id'))

    for d in root.findall('{http://www.iec.ch/61850/2003/SCL}IED'):
        for ln in d.AccessPoint.Server.LDevice.iterchildren():
            if ln.attrib.get('lnType'):
                if ln.attrib.get('lnType') not in LNDataList:
                    print("Bad LNType is on", ln.sourceline, "line")
                    return False
    print("LNDataList", len(LNDataList))
    return True


def DOTypes(scd):
    root = objectify.parse(scd)
    DODataList = []
    for ddt in root.findall('{http://www.iec.ch/61850/2003/SCL}DataTypeTemplates'):
         for do in ddt.DOType:
             if do.attrib.get('id'):
                 DODataList.append(do.attrib.get('id'))

    for ddt in root.findall('{http://www.iec.ch/61850/2003/SCL}DataTypeTemplates'):
        for ln in ddt.LNodeType.iterchildren():
            for do in ln:
                if do.get('type') not in DODataList:
                    print("Bad LNType is on", do.sourceline, "line")
                    return False
    print("DODataList", len(DODataList))
    return True

def newTest(scd):
    root = objectify.parse(scd)
    IEDList = []
    for ied in root.findall('{http://www.iec.ch/61850/2003/SCL}IED'):
        print(ied.get('name'), " ", ied.get('type'))
    return True
