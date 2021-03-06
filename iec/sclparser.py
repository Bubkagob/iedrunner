from lxml import objectify
import subprocess
import time


class SclParser:
    def __init__(self, scd_file):
        root = objectify.parse(scd_file)
        self.__FILENAME = scd_file
        self.__root = root.getroot()
        self.__ddt = self.__root.DataTypeTemplates

    # lxml list
    def __get_subnet_list(self):
        sn_list = []
        try:
            for sn in self.__root.Communication.iterchildren():
                sn_list.append(sn)
            return sn_list
        except:
            return sn_list

    # lxml list
    def get_ap_list(self):
        ap_list = []
        for sn in self.__get_subnet_list():
            for capp in sn.iterchildren():
                ap_list.append(capp)
        return ap_list

    # object ied list
    def get_ied_list(self):
        ied_list = []
        for ied in self.__root.IED:
            ied_list.append(ied)
        return ied_list

    # object LD list
    def __get_ld_list_from_ied(self, ied):
        ld_list = []
        gen = (device for device in ied.AccessPoint.Server.iterchildren()
               if device.get('inst'))
        for device in gen:
            ld_list.append(device)
        return ld_list

    def get_ld_list_from_file(self):
        ld_list = []
        for ied in self.get_ied_list():
            for ld in self.__get_ld_list_from_ied(ied):
                ld_list.append(ld)
        return ld_list

    # IEDname list IED name + inst
    def get_ied_ld_names(self):
        iedname_list = []
        for ied in self.get_ied_list():
            for ld in self.__get_ld_list_from_ied(ied):
                iedname_list.append(ied.get('name')+ld.get('inst'))
        return iedname_list

    # IED_LDname list by IED_LD name
    def get_ied_ld_names_by_ied(self, ied):
        iedname_list = []
        for ld in self.__get_ld_list_from_ied(ied):
            iedname_list.append(ied.get('name')+ld.get('inst'))
        return iedname_list

    # all of AP ip list from Communication block
    def get_ip_list(self):
        ip_list = []
        for ap in self.get_ap_list():
            gen = (address for address in ap.Address.iterchildren() if address.get('type') == 'IP')
            for address in gen:
                ip_list.append(address)
        return ip_list

    #string IEDname by passing ip
    def get_ied_name_by_ip(self, ip):
        for ap in self.get_ap_list():
            gen = (address for address in ap.Address.iterchildren() if address.get('type') == 'IP' and address == ip)
            for address in gen:
                return ap.get('iedName')

    #returns logical devices list by passing concatinated name example TEMPLATELD0
    def get_ld_by_ied_concat_name(self, concat_name):
        ld_list = []
        for ied in self.get_ied_list():
            gen = (ld for ld in self.__get_ld_list_from_ied(ied) if ied.get('name')+ld.get('inst')==concat_name)
            for ld in gen:
                ld_list.append(ld)
        return ld_list

    #returns ied or ieds list by passing IP
    def __get_ied_by_ip(self, ip):
        ied_list=[]
        for ied in self.get_ied_list():
            if ied.get('name') == self.get_ied_name_by_ip(ip):
                ied_list.append(ied)
        return ied_list

    def get_ied_by_iedld_name(self, concat_name):
        for ied in self.get_ied_list():
            gen = (ld for ld in self.__get_ld_list_from_ied(ied) if ied.get('name')+ld.get('inst')==concat_name)
            for ld in gen:
                return ied

    #returns a logical node list from ldevice
    def __get_ln_list_from_ld(self, ld):
        ln_list=[]
        gen = (element for element in ld.iter() if 'lnClass' and 'lnType' in element.attrib)
        for el in gen:
            ln_list.append(el)
        return ln_list

    def __get_doi_list_from_ln(self, ln):
        do_list = []
        for do in ln.DOI:
            do_list.append(do)
        return do_list

    def get_da_names_from_dotype(self, dotype):
        da_list = []
        for da in dotype.iterchildren():
            da_list.append(da.get('name'))
        return da_list

    def check_dai(self, dai, dotype):
        if dai.get('name') in self.get_da_names_from_dotype(dotype):
            return True
        else:
            print("Failed with DAI ckecking === > ", dai.get('name'), "on line", dai.sourceline)
            return False


    def get_da_from_dotype_by_name(self, dotype, daname):
        gen = (datype for datype in dotype.iterchildren() if datype.get('type') and datype.get('name')==daname)
        for el in gen:
            print(el.get('type'))

    def check_sdi(self, sdi, dotype):
        if sdi.get('name') in self.get_da_names_from_dotype(dotype):
            return True
        else:
            print("Failed with SDI ckecking === > ", sdi.get('name'), "on line", sdi.sourceline)
            return False

    def check_dai_sdi(self, doi, dotype):
        for dai in self.__get_dai_list_from_do(doi):
            if not self.check_dai(dai, dotype):
                return False

    def __get_dai_list_from_do(self, do, ):
        dai_list = []
        for i in do.iterchildren(tag='{*}DAI'):
            dai_list.append(i)
        return dai_list

    def __get_sdi_list_from_do(self, do):
        sdi_list = []
        for el in do.iterchildren(tag='{*}SDI'):
            sdi_list.append(el)
        return sdi_list


    # def __get_da_list_from_do(self, do, depth=0):
    #     da_list = []
    #     depth+=1
    #     for i in do.iterchildren():
    #         print("проверяем: \t\t\t глубина = "+str(depth), i.tag,)
    #         print(i.get('name'))
    #         self.__get_da_list_from_do(i, depth)
    #     return da_list


    #gets a bold - like lnode name from server and return lnType from file
    def get_lntype_by_full_ln_name(self, ldevice, full_lnname):
        for lnode in self.__get_ln_list_from_ld(ldevice):
            if full_lnname == self.get_ln_name_inst(lnode):
                return lnode.get('lnType')

    #Lnode full name with instance number
    def get_ln_name_inst(self, lnode):
        if 'prefix' in lnode.attrib:
            if(lnode.get('prefix')):
                return (lnode.get('prefix')+lnode.get('lnClass')+lnode.get('inst'))
            else:
                return (lnode.get('lnClass')+lnode.get('inst'))
        else:
            return lnode.get('lnClass')

    #get Lnode list with Prefix - LnClass - Inst name as in Server
    def __get_ln_name_inst_list_from_ld(self, ldevice):
        res_list = []
        for lnode in self.__get_ln_list_from_ld(ldevice):
            res_list.append(self.get_ln_name_inst(lnode))
        return res_list



    #print all lnType names from file(from all Ldevices)
    def get_ln_list_from_file(self):
        ln_list = []
        for ld in self.get_ied_list():
            for ln in self.__get_ln_list_from_ld(ld):
                ln_list.append(ln)
        return ln_list
                #self.get_lntype_by_id(ln.get('lnType'))
                #self.get_doi_from_ln(ln)


    #print all LNodeType names from file
    def get_lntype_list_from_file(self):
        res_list = []
        for lntype in self.__ddt.LNodeType:
            res_list.append(lntype)
        return res_list

    #print all DOType names from file
    def get_dotype_list_from_file(self):
        res_list = []
        for do_type in self.__ddt.DOType:
            res_list.append(do_type)
        return res_list

    #print all DAType names from file
    def get_datype_list_from_file(self):
        res_list = []
        for da_type in self.__ddt.DAType:
            res_list.append(da_type)
        return res_list

    #print all DAType names from file
    def get_enum_list_from_file(self):
        res_list = []
        for enum in self.__ddt.EnumType:
            res_list.append(enum)
        return res_list

    def get_all_typelist_from_file(self):
        res_list = []
        for lntype in self.__ddt.LNodeType:
            res_list.append(lntype)
        for do_type in self.__ddt.DOType:
            res_list.append(do_type)
        for da_type in self.__ddt.DAType:
            res_list.append(da_type)
        for enum in self.__ddt.EnumType:
            res_list.append(enum)
        return res_list

    def get_datatype_by_id(self, typid):
        gen = (datatype for datatype in self.get_all_typelist_from_file() if datatype.get('id')==typid)
        for datatype in gen:
            return datatype

    def get_dotype_by_id(self, dotypeid):
        gen = (dotype for dotype in self.get_dotype_list_from_file() if dotype.get('id')==dotypeid)
        for do_type in gen:
            return do_type

    def get_datype_by_id(self, datypeid):
        gen = (datype for datype in self.get_datype_list_from_file() if datype.get('id')==datypeid)
        for da_type in gen:
            return da_type

    def get_enum_by_id(self, enumid):
        gen = (enumtype for enumtype in self.get_enum_list_from_file() if enumtype.get('id')==enumid)
        for enum in gen:
            return enum



    def get_dotype_from_lntype_by_name(self, lntype, doiname):
        gen = (do for do in lntype.DO if do.get('name')==doiname)
        for el in gen:
            return self.__get_dotypeobj_by_id(el.get('type'))

    def __get_dotypeobj_by_id(self, dotypeid):
        gen = (dotype for dotype in self.__ddt.DOType if dotype.get('id')==dotypeid)
        for dotype in gen:
            return dotype

    def get_dotypelist_from_lntype_by_lnid(self, lnid):
        do_list = []
        gen = (lntype for lntype in self.__ddt.LNodeType if lntype.get('id')==lnid)
        for lnodetype in gen:
            for do in lnodetype.iterchildren():
                do_list.append(do.get('name'))
        return do_list

    def get_do_name_list_from_lntype(self, lnodetype):
        do_list = []
        for do in lnodetype.iterchildren():
            do_list.append(do.get('name'))
        return do_list

    def get_dotype_list_from_lntype(self, lnodetype):
        do_list = []
        for do in lnodetype.iterchildren():
            do_list.append(do.get('type'))
        return do_list

    def get_do_list_from_lntype(self, lnodetype):
        do_list = []
        for do in lnodetype.iterchildren():
            do_list.append(do)
        return do_list

    def get_lntype_by_id(self, idtype):
        gen = (lntype for lntype in self.__ddt.LNodeType if lntype.get('id')==idtype)
        for lnodetype in gen:
            return lnodetype

    def get_lntype_by_lnclass(self, ln_class):
        gen = (lntype for lntype in self.__ddt.LNodeType if lntype.get('lnClass')==ln_class)
        for lnodetype in gen:
            return lnodetype

    def get_ds_list_from_ld(self, ld):
        ds_list=[]
        for ds in ld.LN0.iterchildren(tag='{*}DataSet'):
            ds_list.append(ds)
        return ds_list

    def get_dataset_from_ld_by_name(self, ld, name):
        ds_list = self.get_ds_list_from_ld(ld)
        for ds in ds_list:
            if ds.get('name')==name:
                return ds
        return ('Fail on', ds.sourceline)

    def get_dsnames_list_from_ld(self, ld):
        ds_list=[]
        for ds in ld.LN0.iterchildren(tag='{*}DataSet'):
            ds_list.append(ds.get('name'))
        return ds_list

    def get_rc_list_from_ld(self, ld):
        rc_list=[]
        for rc in ld.LN0.iterchildren(tag='{*}ReportControl'):
            rc_list.append(rc)
        return rc_list

        rc_names = []
        if hasattr(rc, 'RptEnabled'):
            report_num = int(rc.RptEnabled.get('max'))
            for i in range(report_num):
                if report_num < 8:
                    rcname = rc.get('name')+'0'+str(i+1)
                else:
                    rcname = rc.get('name')+str(i+1)
                rc_names.append(rcname)
        else:
            rc_names.append(rc.get('name')+'01')
        return rc_names



    def get_fcda_list_from_ds(self, ds):
        fcda_list = []
        for fcda in ds.iterchildren(tag='{*}FCDA'):
            fcda_list.append(fcda)
        return fcda_list

    def get_fcda_varlist_from_ds(self, ds):
        var_fcda=[]
        for fcda in self.get_fcda_list_from_ds(ds):
            print(fcda.sourceline)
            var_fcda.append(self.get_ln_name_from_fcda(fcda)+'.'+fcda.get('doName'))
        return var_fcda

    def get_full_fcda_varlist(self):
        var_fcda=[]
        for ied in self.get_ied_list():
            for ld in self.__get_ld_list_from_ied(ied):
                for ds in self.get_ds_list_from_ld(ld):
                    for fcda in self.get_fcda_list_from_ds(ds):
                        print(fcda.sourceline)
                        var_fcda.append(ied.get('name')+ld.get('inst')+'/'+self.get_ln_name_from_fcda(fcda)+'.'+fcda.get('doName'))
        return var_fcda


    def get_ln_name_from_fcda(self, fcda):
        if fcda.get('prefix'):
            return (fcda.get('prefix')+fcda.get('lnClass')+fcda.get('lnInst'))
        else:
            if fcda.get('lnInst'):
                return (fcda.get('lnClass')+fcda.get('lnInst'))
            else:
                return (fcda.get('lnClass'))


    def var_collecter(self, dotype, name='', tempd={}, fc=''):
        temp_dict = tempd
        fc_name=fc
        for da in dotype.iterchildren():
            if(da.get('fc')):
                fc_name = da.get('fc')
            if not da.get('type') or (da.get('type') and da.get('bType')=='Enum'):
                temp_dict[name+'.'+da.get('name')]=fc_name
            else:
                self.var_collecter(self.get_datatype_by_id(da.get('type')), name+'.'+da.get('name'), temp_dict, fc_name)
        return temp_dict


    def get_rcb_full_names(self):
        for ied in self.get_ied_list():
            for ld in self.__get_ld_list_from_ied(ied):
                ds_list = self.get_ds_list_from_ld(ld)
                for rc in self.get_rc_list_from_ld(ld):
                    if rc.get('buffered') and rc.get('buffered')=='true':
                        is_buffered = '.BR.'
                    else:
                        is_buffered = '.RP.'
                    for cb in self.get_rcname_list_from_rc(rc):
                        print('*********REPORT CONTROL*********')
                        print(ied.get('name')+ld.get('inst')+'/LLN0'+is_buffered+cb, rc.sourceline)
                        print('*********MEMBERS*********')
                        ds = self.get_dataset_from_ld_by_name(ld, rc.get('datSet'))
                        for fcda in self.get_fcda_list_from_ds(ds):
                            lntype = self.get_lntype_by_lnclass(fcda.get('lnClass'))
                            var_list_from_node = {}
                            lninst = ied.get('name')+ld.get('inst')+'/'+self.get_ln_name_from_fcda(fcda)+'.'
                            for do in self.get_do_list_from_lntype(lntype):
                                dotype = self.__get_dotypeobj_by_id(do.get('type'))
                                if do.get('name')==fcda.get('doName'):
                                    var_list_from_node.update(self.var_collecter(dotype, name=lninst+do.get('name'), tempd={}))
                            print('\t\t\tLNODE TYPE---' , lntype.get('id'))
                            print('********* DO *********')
                            print(ied.get('name')+ld.get('inst')+'/'+self.get_ln_name_from_fcda(fcda)+'.'+fcda.get('doName'))
                            print('\t\tVariables: ')
                            for k, v in var_list_from_node.items():
                                print(k, v)




    def get_do_type_by_id_from_lntype(self, lnodetype, doi_name):
        gen = (dotype for dotype in lnodetype.iterchildren() if dotype.get('name')==doi_name)
        for do in gen:
            return self.get_dotype_by_id(do.get('type'))

    def get_sdo_type_by_id_from_dotype(self, lnodetype, doi_name):
        gen = (dotype for dotype in lnodetype.iterchildren() if dotype.get('name')==doi_name)
        for do in gen:
            return self.get_dotype_by_id(do.get('type'))

    def get_sdolist_from_dotype(self, dotype):
        sdo_list=[]
        for sdo in dotype.iterdescendants(tag='{*}SDO'):
            sdo_list.append(sdo)
        return sdo_list

    def get_dalist_from_dotype(self, dotype):
        do_list=[]
        for do in dotype.iterdescendants(tag='{*}DA'):
            do_list.append(do)
        return do_list




    # ========= 0 предварительная проверка LNodeTypes
    def is_lnode_types_ok(self):
        req_ln = ['id', 'lnClass']
        req_dotype = ['name', 'type']
        for lnodetype in self.get_lntype_list_from_file():
            if not set(req_ln) <= set(lnodetype.keys()):
                print("Not enough attributes in LNodeType on line", lnodetype.sourceline)
                return False
            for do_type in lnodetype.iterchildren():
                if not set(req_dotype) <= set(do_type.keys()):
                    print("Not enough attributes in DOType on line", do_type.sourceline)
                    return False
                if self.get_dotype_by_id(do_type.get('type')) is None:
                    print("Cannot find DOType for DO on line", do_type.sourceline, "from LNodeType", lnodetype.get('id'), "on line", lnodetype.sourceline)
                    return False
        return True

    # ========= 0 предварительная проверка DOTypes
    def is_do_types_ok(self):
        req_dotype = ['cdc', 'id']
        req_da = ['fc', 'bType', 'name']
        req_sdo = ['name', 'type']
        for dotype in self.get_dotype_list_from_file():
            if not set(req_dotype) <= set(dotype.keys()):
                print("Not enough attributes in DOType on line", dotype.sourceline)
                return False
            for da in dotype.iterdescendants(tag='{*}DA'):
                if not set(req_da) <= set(da.keys()):
                    print("Not enough attributes in DA on line", da.sourceline, "from DOType", dotype.get('id'), "on line", dotype.sourceline)
                    return False
                if 'type' in da.keys() and da.get('bType')=='Struct':
                    if self.get_datype_by_id(da.get('type')) is None:
                        print("Cannot find DAType for DA with Structure on line", da.sourceline, "from DOType", dotype.get('id'), "on line", dotype.sourceline)
                        return False
                if 'type' in da.keys() and da.get('bType')=='Enum':
                    if self.get_enum_by_id(da.get('type')) is None:
                        print("Cannot find EnumType for DA with Enumeration on line", da.sourceline, "from DOType", dotype.get('id'), "on line", dotype.sourceline)
                        return False
            for sdo in dotype.iterdescendants(tag='{*}SDO'):
                if not set(req_sdo) <= set(sdo.keys()):
                    print("Not enough attributes in SDO on line", sdo.sourceline, "from DOType", dotype.get('id'), "on line", dotype.sourceline)
                    return False
                if self.get_dotype_by_id(sdo.get('type')) is None:
                    print("Cannot find DOType for SDO on line", sdo.sourceline, "from DOType", dotype.get('id'), "on line", dotype.sourceline)
                    return False
        return True

    # ========= 0 предварительная проверка LNodeTypes
    def is_da_types_ok(self):
        req_bda = ['bType', 'name']
        for datype in self.get_datype_list_from_file():
            if not 'id' in datype.keys() or datype.get('id')=='':
                print("Not enough ID attribute or it is empty in DAType on line", datype.sourceline)
                return False
            for bda in datype.iterdescendants():
                if not set(req_bda) <= set(bda.keys()):
                    print("Not enough attributes in BDA on line", bda.sourceline, "from DAType", datype.get('id'), "on line", datype.sourceline)
                    return False
                for key in bda.keys():
                    if bda.get(key)=='':
                        print(key, "attribute is empty in BDA on line", bda.sourceline)
                        return False
                if 'type' in bda.keys() and bda.get('bType')=='Struct':
                    if self.get_datype_by_id(bda.get('type')) is None:
                        print("Cannot find DAType for BDA with Structure on line", bda.sourceline, "from DAType", datype.get('id'), "on line", datype.sourceline)
                        return False
                if 'type' in bda.keys() and bda.get('bType')=='Enum':
                    if self.get_enum_by_id(bda.get('type')) is None:
                        print("Cannot find EnumType for BDA with Enumeration on line", bda.sourceline, "from DAType", datype.get('id'), "on line", datype.sourceline)
                        return False
        return True

    def is_enum_types_ok(self):
        for enumtype in self.get_enum_list_from_file():
            if not 'id' in enumtype.keys() or enumtype.get('id')=='':
                print("Not enough ID attribute or it is empty in EnumType on line", enumtype.sourceline)
                return False
            for enumval in enumtype.iterdescendants():
                if not 'ord' in enumval.keys() or enumval.get('ord')=='':
                    print("Not enough ORD attribute or it is empty in EnumVal on line", enumval.sourceline, "from EnumType", enumtype.get('id'), "on line", enumtype.sourceline)
                    return False
        return True

    # ========= 2 IED Присутствуют обязательные параметры
    def is_all_attributes_in_ied_is_ok(self):
        req = ['name', 'type', 'manufacturer', 'configVersion']
        for ied in self.get_ied_list():
            if not set(req) <= set(ied.keys()):
                print("Not enough attributes in IED on line", ied.sourceline)
                return False
            for key in ied.keys():
                if ied.get(key)=='':
                    print(key, "attribute is empty in IED on line", ied.sourceline)
                    return False
        return True

    # ========= 3 LN Присутствуют обязательные параметры
    def is_all_attributes_in_ln_is_ok(self):
        req = ['inst', 'lnClass', 'lnType']
        for ln in self.get_ln_list_from_file():
            if not set(req) <= set(ln.keys()) :
                print("Not enough attributes in LN on line", ln.sourceline)
                return False
            for key in ln.keys():
                if ln.get(key)=='':
                    if key in ['inst', 'prefix']: #for LN0 and without prefix nodes
                        continue
                    print(key, "attribute is empty in LN on line", ln.sourceline)
                    return False
        return True

    # ========= 4 DS Присутствуют обязательные параметры
    def is_all_attributes_in_ds_is_ok(self):
        req = ['name', 'desc']
        req_fcda = ['doName', 'fc', 'ldInst', 'lnClass']
        for ld in self.get_ld_list_from_file():
            for ds in self.get_ds_list_from_ld(ld):
                if not set(req) <= set(ds.keys()) :
                    print("Not enough attributes in DS on line", ds.sourceline)
                    return False
                for key in ds.keys():
                    if ds.get(key)=='':
                        if key in ['desc']: #for LN0 and without prefix nodes
                            continue
                        print(key, "attribute is empty in DataSet on line", ds.sourceline)
                        return False
                for fcda in self.get_fcda_list_from_ds(ds):
                    if not set(req_fcda) <= set(fcda.keys()) :
                        print("Not enough attributes in FCDA on line", fcda.sourceline)
                        return False
                    for key in fcda.keys():
                        if fcda.get(key)=='':
                            print(key, "attribute is empty in FCDA on line", fcda.sourceline, "from DataSet on line", ds.sourceline)
                            return False
        return True

    # ========= 5 в DS указаны правильные привязки к lnode
    def is_all_ds_targets_is_ok(self):
        for ld in self.get_ld_list_from_file():
            ln_list = self.__get_ln_name_inst_list_from_ld(ld)
            for ds in self.get_ds_list_from_ld(ld):
                for fcda in self.get_fcda_list_from_ds(ds):
                    fcda_ref = self.get_ln_name_from_fcda(fcda)
                    if not fcda_ref in ln_list:
                        print("Unlinked FCDA ", fcda_ref, "on line",fcda.sourceline)
                        return False
        return True

    # ========= 6 в RC Присутствуют обязательные параметры
    def is_all_attributes_in_rc_is_ok(self):
        req = ['bufTime', 'buffered', 'confRev', 'datSet', 'name']
        req_of = ['configRef', 'dataSet', 'reasonCode', 'seqNum', 'timeStamp']
        req_trg = ['dchg', 'period', 'qchg']
        for ld in self.get_ld_list_from_file():
            for rc in self.get_rc_list_from_ld(ld):
                if not set(req) <= set(rc.keys()) :
                    print("Not enough attributes in RC on line", rc.sourceline, "from LDevice on line", ld.sourceline)
                    return False
                for key in rc.keys():
                    if rc.get(key)=='':
                        if key in ['desc']: #for LN0 and without prefix nodes
                            continue
                        print(key, "attribute is empty in ReportControl on line", rc.sourceline, "from LDevice on line", ld.sourceline)
                        return False
                for trg in rc.iterdescendants(tag='{*}TrgOps'):
                    if not set(req_trg) <= set(trg.keys()) :
                        print("Not enough attributes in TrgOps block on line", trg.sourceline, "from ReportControl on line", rc.sourceline, "from LDevice on line", ld.sourceline)
                        return False
                    for key in trg.keys():
                        if trg.get(key)=='':
                            print(key, "attribute is empty in TrgOps block on line", trg.sourceline, "from ReportControl on line", rc.sourceline, "from LDevice on line", ld.sourceline)
                            return False
                for of in rc.iterdescendants(tag='{*}OptFields'):
                    if not set(req_of) <= set(of.keys()) :
                        print("Not enough attributes in OptFields block on line", of.sourceline, "from ReportControl on line", rc.sourceline, "from LDevice on line", ld.sourceline)
                        return False
                    for key in of.keys():
                        if of.get(key)=='':
                            print(key, "attribute is empty in OptFields block on line", of.sourceline, "from ReportControl on line", rc.sourceline, "from LDevice on line", ld.sourceline)
                            return False
        return True

    # ========= 7 в RC Присутствуют ссылки на dset
    def is_all_report_control_linked(self):
        for ld in self.get_ld_list_from_file():
            for rc in self.get_rc_list_from_ld(ld):
                if not rc.get('datSet') in self.get_dsnames_list_from_ld(ld):
                    print("Unlinked ReportControl Block on line", rc.sourceline)
                    return False
        return True

    # ========= 8 в DO (from LNodeType) Присутствуют обязательные параметры
    def is_all_attributes_in_do_is_ok(self):
        req = ['name', 'type']
        for lntype in self.get_lntype_list_from_file():
            for do in lntype.iterchildren():
                if not set(req) <= set(do.keys()):
                    print("Not enough attributes in DO on line", do.sourceline, "from LNodeType", lntype.get('id'))
                    return False
        return True

    # ========= 9 test Присутствуют все типы, используемые в ied
    def is_all_types_is_ok(self):
        for ied in self.get_ied_list():
            for ld in self.__get_ld_list_from_ied(ied):
                for ln in self.__get_ln_list_from_ld(ld):
                    lnodetype = self.get_lntype_by_id(ln.get('lnType'))
                    dotype_list = self.get_do_name_list_from_lntype(lnodetype)
                    for doi in self.__get_doi_list_from_ln(ln):
                        dotype = self.get_dotype_from_lntype_by_name(lnodetype, doi.get('name'))
                        if not doi.get('name') in dotype_list:
                            print("DOI ", doi.get('name'), "from line ", doi.sourceline, "not in LNodeType", ln.get('lnType'))
                            return False
                        for dai in self.__get_dai_list_from_do(doi):
                            if not self.check_dai(dai, dotype):
                                return False
                        for sdi in self.__get_sdi_list_from_do(doi):
                            if not self.check_sdi(sdi, dotype):
                                return False
        return True

    # ========= FULL test Присутствуют все типы, используемые в ied
    def is_all_params_in(self):
        for ied in self.get_ied_list():
            for ld in self.__get_ld_list_from_ied(ied):
                for ln in self.__get_ln_list_from_ld(ld):
                    lntype = self.get_lntype_by_id(ln.get('lnType'))
                    do_list = self.get_do_name_list_from_lntype(lntype)
                    for doi in self.__get_doi_list_from_ln(ln):
                        if not doi.get('name'):
                            print("DOI does not have a NAME attribute on line", doi.sourceline, " from LN ", ln.get('lnType'))
                            return False
                        if not doi.get('name') in do_list:
                            print("DOI ", doi.get('name'), "from line ", doi.sourceline, "not in LNodeType", ln.get('lnType'))
                            return False
                        do_type = self.get_do_type_by_id_from_lntype(lntype, doi.get('name'))
                        for dai in self.__get_dai_list_from_do(doi):
                            for key in dai.keys():
                                if dai.get(key)=='':
                                    print(key, "attribute is empty in DAI on line", dai.sourceline, "from LN on line", ln.get('lnType'))
                                    return False
                            if not dai.get('name'):
                                print("DAI does not have a NAME attribute on line", dai.sourceline, "from DOI", doi.get('name'), "from LN on line", ln.get('lnType'))
                                return False
                            if not dai.get('name') in self.get_da_names_from_dotype(do_type):
                                 print("DAI from line", dai.sourceline, "has an unknown name, not from specific DOType", do_type.get('id'), "from line", do_type.sourceline)
                                 return False
                        for sdi in self.__get_sdi_list_from_do(doi):
                            for key in sdi.keys():
                                if sdi.get(key)=='':
                                    print(key, "attribute is empty in SDI on line", sdi.sourceline, "from LN on line", ln.get('lnType'))
                                    return False
                            if not sdi.get('name'):
                                print("SDI does not have a NAME attribute on line", sdi.sourceline, "from DOI", doi.get('name'), "from LN on line", ln.get('lnType'))
                                return False
                            sdo_type = self.get_do_type_by_id_from_lntype(lntype, doi.get('name'))
                            if not sdi.get('name') in self.get_da_names_from_dotype(sdo_type):
                                 print("SDI from line", sdi.sourceline, "has an unknown name, not from specific DOType", sdo_type.get('id'), "from line", sdo_type.sourceline)
                                 return False
        return True


    # ========= IECTestCase # test Присутствуют обязательные параметры
    def is_structure_equal(self, ied_ld_name, clt):
        ied = self.get_ied_by_iedld_name(ied_ld_name)
        ied_ld_list_from_file = self.get_ied_ld_names_by_ied(ied)
        for ld in clt.get_ld_list():
            ld_server_name = clt.get_name_of(ld)
            if not ld_server_name in ied_ld_list_from_file:
                print("Achtung! ===> " , ld_server_name, "not in file")
                return False
            for ldevice in self.get_ld_by_ied_concat_name(clt.get_name_of(ld)):
                ln_list_by_ld = self.__get_ln_name_inst_list_from_ld(ldevice=ldevice)
                for ln_srv in clt.get_ln_list_from_ld(ld):
                    node_name_from_server = clt.get_name_of(ln_srv)
                    if not node_name_from_server in ln_list_by_ld:
                        print("Caramba! ===> " , node_name_from_server, "not in file")
                        return False
                    if not set(clt.get_dobject_names(ld, ln_srv)) == set(self.get_dotypelist_from_lntype_by_lnid(self.get_lntype_by_full_ln_name(ldevice, node_name_from_server))):
                        print("Not equals dataobjects in lnode ", node_name_from_server, "from LDevice", ld_server_name)
                        return False
        return True

    def is_rc_names_correct_in_server(self, ied_ld_name, clt):
        ied = self.get_ied_by_iedld_name(ied_ld_name)
        for ld in self.__get_ld_list_from_ied(ied):
            rcbr_names_from_server = clt.get_rcbr_list_by_ldname(ied.get('name')+ld.get('inst'))
            rcrp_names_from_server = clt.get_rcrp_list_by_ldname(ied.get('name')+ld.get('inst'))
            rcnames_from_server = rcbr_names_from_server + rcrp_names_from_server
            for rcontrol in self.get_rc_list_from_ld(ld):
                rc_names_from_file = self.get_rcname_list_from_rc(rcontrol)
                for rcname in rc_names_from_file:
                    if not rcname in rcnames_from_server:
                        print("ReportControl", rcname, "from line", rcontrol.sourceline, "not in",ied.get('name')+ld.get('inst'),"from Server")
                        clt.stop()
                        return False
        return True

    # def get_rcname_list_from_rc(self, rc):
    #     rc_names = []
    #     if hasattr(rc, 'RptEnabled'):
    #         report_num = int(rc.RptEnabled.get('max'))
    #         for i in range(report_num):
    #             if report_num < 8:
    #                 rcname = rc.get('name')+'0'+str(i+1)
    #             else:
    #                 rcname = rc.get('name')+str(i+1)
    #             rc_names.append(rcname)
    #     else:
    #         rc_names.append(rc.get('name')+'01')
    #     return rc_names
    def get_rcname_list_from_rc(self, rc):
        rc_names = []
        if hasattr(rc, 'RptEnabled'):
            report_num = int(rc.RptEnabled.get('max'))
            for i in range(report_num):
                if report_num < 8:
                    rcname = rc.get('name')+'0'+str(i+1)
                else:
                    rcname = rc.get('name')+str(i+1)
                rc_names.append(rcname)
        else:
            rc_names.append(rc.get('name')+'01')
        return rc_names


    def test_rc_attributes_ok_in_server(self, ied_ld_name, clt):
        ied = self.get_ied_by_iedld_name(ied_ld_name)
        for ld in self.__get_ld_list_from_ied(ied):
            for rcontrol in self.get_rc_list_from_ld(ld):
                rc_names_from_file = self.get_rcname_list_from_rc(rcontrol)
                for rc_dict_from_file in self.get_all_reports_dicts_list_from_rc(rcontrol):
                    for rc_name in rc_names_from_file:
                        if rcontrol.get('buffered')=='true':
                            rpt_name = ied.get('name')+ld.get('inst')+'/LLN0.BR.'+rc_name
                        else:
                            rpt_name = ied.get('name')+ld.get('inst')+'/LLN0.RP.'+rc_name
                        rc_dict_from_server = clt.get_rcb_dictionary(rpt_name)
                        for k in rc_dict_from_file:
                            if not rc_dict_from_file[k] == rc_dict_from_server[k]:
                                print("ReportControl attr:", k, "from RCB", rpt_name, "from line", rcontrol.sourceline, "not equal with same attribute in", ied_ld_name,"instance from Server")
                                print(rc_dict_from_file[k], "Ouch", k, rc_dict_from_server[k])
                                print(type(rc_dict_from_file[k]), "Ouch", k, type(rc_dict_from_server[k]))
                                return False
        return True


    def var_fc_builder(self, dotype, name='', tempd={}, fc=''):
        temp_dict = tempd
        fc_name=fc
        for da in dotype.iterchildren():
            if(da.get('fc')):
                fc_name = da.get('fc')
            if not da.get('type') or (da.get('type') and da.get('bType')=='Enum'):
                temp_dict[name+'.'+da.get('name')]=fc_name
                #temp_dict.append(name+'.'+da.get('name')+'['+da.get('bType')+']'+'+++++++++++++++++++'+fc_name)
                #print('\t\t\t', name+'.'+da.get('name')+'['+da.get('bType')+']' , da.sourceline)
            else:
                self.var_fc_builder(self.get_datatype_by_id(da.get('type')), name+'.'+da.get('name'), temp_dict, fc_name)
        return temp_dict

    def convert_btype_name(self, btype):
        if btype in ['FLOAT32']:
            return 'float'
        if btype == 'Struct':
            return 'structure'
        if btype == 'BOOLEAN':
            return 'boolean'
        if btype in ['Enum', 'INT32', 'INT128']:
            return 'integer'
        if btype == 'Timestamp':
            return 'utc-time'
        if btype == 'VisString255':
            return 'visible-string'
        if btype in ['INT32U', 'INT8U']:
            return 'unsigned'
        if btype in ['Octet64']:
            return 'octet-string'
        if btype in ['Check', 'Quality', 'Dbpos']:
            return 'bit-string'
        else:
            return '------------------------------------------------'

    def get_flow_max_var(self, btype):
        max_int_8   = 127
        max_uint8   = 255
        max_uint_16 = 65535
        max_int16   = 32767
        max_uint32  = 4294967295
        max_int32   = 2147483647
        max_uint64  = 18446744073709551615
        max_int64   = 9223372036854775807
        max_float   = 123.456
        max_time = 4294967295999
        quality = 8191
        if btype == 'INT16':
            return 'int16 '+ str(max_int16)
        if btype in ['INT32', 'Enum', 'Check', 'Dbpos']:
            return 'int32 '+ str(max_int32)
        if btype in ['INT8U', 'BOOLEAN']:
            return 'uint8 '+ str(max_uint8)
        if btype == 'INT16U':
            return 'uint16 '+ str(max_uint_16)
        if btype == 'INT32U':
            return 'uint32 '+ str(max_uint32)
        if btype in ['FLOAT32']:
            return 'f32 '+ str(max_float)
        if btype == 'Timestamp':
            return 'uint64 '+ str(max_time)
        if btype == 'Quality':
            return 'uint16 '+ str(quality)

    def get_flow_min_var(self, btype):
        max_int_8   = -128
        max_uint8   = 0
        max_uint_16 = 0
        max_int16   = -32768
        max_uint32  = 0
        max_int32   = -2147483648
        max_uint64  = 0
        max_int64   = -9223372036854775808
        max_float   = -123.456
        max_time = 0
        quality = 0
        if btype == 'INT16':
            return 'int16 '+ str(max_int16)
        if btype in ['INT32', 'Enum', 'Check', 'Dbpos']:
            return 'int32 '+ str(max_int32)
        if btype in ['INT8U', 'BOOLEAN']:
            return 'uint8 '+ str(max_uint8)
        if btype == 'INT16U':
            return 'uint16 '+ str(max_uint_16)
        if btype == 'INT32U':
            return 'uint32 '+ str(max_uint32)
        if btype in ['FLOAT32']:
            return 'f32 '+ str(max_float)
        if btype == 'Timestamp':
            return 'uint64 '+ str(max_time)
        if btype == 'Quality':
            return 'uint16 '+ str(quality)

    def get_flow_avg_var(self, btype):
        max_int_8   = 100
        max_uint8   = 111
        max_uint_16 = 33333
        max_int16   = 12345
        max_uint32  = 2345678901
        max_int32   = 1234567891
        max_uint64  = 9223372036854775807
        max_int64   = 4567891234567891234
        max_float   = 23.456
        max_time = 2142524142444
        quality = 4040
        if btype == 'INT16':
            return 'int16 '+ str(max_int16)
        if btype in ['INT32', 'Enum', 'Check', 'Dbpos']:
            return 'int32 '+ str(max_int32)
        if btype in ['INT8U', 'BOOLEAN']:
            return 'uint8 '+ str(max_uint8)
        if btype == 'INT16U':
            return 'uint16 '+ str(max_uint_16)
        if btype == 'INT32U':
            return 'uint32 '+ str(max_uint32)
        if btype in ['FLOAT32']:
            return 'f32 '+ str(max_float)
        if btype == 'Timestamp':
            return 'uint64 '+ str(max_time)
        if btype == 'Quality':
            return 'uint16 '+ str(quality)



    def var_type_maxvalue_builder(self, dotype, name='', tempd={}, bt=''):
        temp_dict = tempd
        btype_name=bt
        for da in dotype.iterchildren():
            if(da.get('bType')):
                btype_name = self.get_flow_max_var(da.get('bType'))
            if not da.get('type') or (da.get('type') and da.get('bType')=='Enum'):
                if not btype_name == None:
                    temp_dict[name+'.'+da.get('name')]=btype_name
            else:
                self.var_type_maxvalue_builder(self.get_datatype_by_id(da.get('type')), name+'.'+da.get('name'), temp_dict, btype_name)
        return temp_dict

    def var_type_minvalue_builder(self, dotype, name='', tempd={}, bt=''):
        temp_dict = tempd
        btype_name=bt
        for da in dotype.iterchildren():
            if(da.get('bType')):
                btype_name = self.get_flow_min_var(da.get('bType'))
            if not da.get('type') or (da.get('type') and da.get('bType')=='Enum'):
                if not btype_name == None:
                    temp_dict[name+'.'+da.get('name')]=btype_name
            else:
                self.var_type_minvalue_builder(self.get_datatype_by_id(da.get('type')), name+'.'+da.get('name'), temp_dict, btype_name)
        return temp_dict

    def var_type_avgvalue_builder(self, dotype, name='', tempd={}, bt=''):
        temp_dict = tempd
        btype_name=bt
        for da in dotype.iterchildren():
            if(da.get('bType')):
                btype_name = self.get_flow_avg_var(da.get('bType'))
            if not da.get('type') or (da.get('type') and da.get('bType')=='Enum'):
                if not btype_name == None:
                    temp_dict[name+'.'+da.get('name')]=btype_name
            else:
                self.var_type_avgvalue_builder(self.get_datatype_by_id(da.get('type')), name+'.'+da.get('name'), temp_dict, btype_name)
        return temp_dict

    def var_btype_builder(self, dotype, name='', tempd={}, bt=''):
        temp_dict = tempd
        btype_name=bt
        for da in dotype.iterchildren():
            if(da.get('bType')):
                btype_name = da.get('bType')
            if not da.get('type') or (da.get('type') and da.get('bType')=='Enum'):
                temp_dict[name+'.'+da.get('name')]=self.convert_btype_name(btype_name)
                #temp_dict.append(name+'.'+da.get('name')+'['+da.get('bType')+']'+'+++++++++++++++++++'+fc_name)
                #print('\t\t\t', name+'.'+da.get('name')+'['+da.get('bType')+']' , da.sourceline)
            else:
                self.var_btype_builder(self.get_datatype_by_id(da.get('type')), name+'.'+da.get('name'), temp_dict, btype_name)
        return temp_dict

    def test_lnode_fc_parameters_is_ok(self, ied_ld_name, clt):
        ied = self.get_ied_by_iedld_name(ied_ld_name)
        for ld in self.__get_ld_list_from_ied(ied):
            #print(ld.get('inst'))
            for ln in self.__get_ln_list_from_ld(ld=ld):
                lntype = self.get_lntype_by_id(ln.get('lnType'))
                lninst = ied.get('name')+ld.get('inst')+'/'+self.get_ln_name_inst(ln)
                #print('\t'+lntype.get('id'))
                var_list_from_node = {}
                for do in self.get_do_list_from_lntype(lntype):
                    dotype = self.__get_dotypeobj_by_id(do.get('type'))
                    var_list_from_node.update(self.var_fc_builder(dotype=dotype, name=lninst+'.'+do.get('name'), tempd={}))
                var_list_from_server = clt.get_varlist_fc_by_ld_lnname(lninst)
                for k in var_list_from_node:
                    try:
                        if not var_list_from_node[k] == var_list_from_server[k]:
                            print('FC not equal in', k, 'variable')
                            return False
                    except KeyError as e:
                        print('Variable not in a Server: ', str(e) )
                        return False
        return True

#'''
###############################          CHECK bTypes
#'''

    def test_lnode_btype_parameters_is_ok(self, ied_ld_name, clt):
        ied = self.get_ied_by_iedld_name(ied_ld_name)
        for ld in self.__get_ld_list_from_ied(ied):
            for ln in self.__get_ln_list_from_ld(ld=ld):
                lntype = self.get_lntype_by_id(ln.get('lnType'))
                lninst = ied.get('name')+ld.get('inst')+'/'+self.get_ln_name_inst(ln)
                var_list_from_node = {}
                for do in self.get_do_list_from_lntype(lntype):
                    dotype = self.__get_dotypeobj_by_id(do.get('type'))
                    var_list_from_node.update(self.var_btype_builder(dotype=dotype, name=lninst+'.'+do.get('name'), tempd={}))
                var_list_from_server = clt.get_varlist_bytype_by_ld_lnname(lninst)
                for k in var_list_from_node:
                    try:
                        if not var_list_from_node[k] == var_list_from_server[k]:
                            print('bType not equal in', k, 'variable')
                            return False
                    except KeyError as e:
                        print('Variable not in a Server: ', str(e) )
                        return False
        return True

    def sas_client(self, filename):
        client = '/tmp/rattlehead/tmp/test-tools/test-client'
        connection = 'conn1'
        timeout = str(0)
        cmd = client+' --connection='+connection+' --file='+filename+' --timeout='+timeout +' > /dev/null'
        proc = subprocess.run(cmd, shell = True)

    def test_var_storm(self, ied_ld_name, clt):
        ied = self.get_ied_by_iedld_name(ied_ld_name)
        var_max_list = {}
        var_min_list = {}
        var_avg_list = {}
        for ld in self.__get_ld_list_from_ied(ied):
            for ln in self.__get_ln_list_from_ld(ld=ld):
                lntype = self.get_lntype_by_id(ln.get('lnType'))
                lninst = ied.get('name')+ld.get('inst')+'/'+self.get_ln_name_inst(ln)
                for do in self.get_do_list_from_lntype(lntype):
                    dotype = self.__get_dotypeobj_by_id(do.get('type'))
                    var_max_list.update(self.var_type_maxvalue_builder(dotype=dotype, name=lninst+'.'+do.get('name'), tempd={}))
                    var_min_list.update(self.var_type_minvalue_builder(dotype=dotype, name=lninst+'.'+do.get('name'), tempd={}))
                    var_avg_list.update(self.var_type_avgvalue_builder(dotype=dotype, name=lninst+'.'+do.get('name'), tempd={}))
                f = open(ied_ld_name+'_max.txt', 'w')
                for k, v in var_max_list.items():
                    f.write(k+' '+v+'\n')
                f.close()
                f = open(ied_ld_name+'_min.txt', 'w')
                for k, v in var_min_list.items():
                    f.write(k+' '+v+'\n')
                f.close()
                f = open(ied_ld_name+'_avg.txt', 'w')
                for k, v in var_avg_list.items():
                    f.write(k+' '+v+'\n')
                f.close()
        for flow_file in [ied_ld_name+'_max.txt', ied_ld_name+'_min.txt', ied_ld_name+'_avg.txt']:
            self.sas_client(flow_file)
            self.checker(flow_file, clt)
        return True


    def get_vars_fc(self):
        for ied in self.get_ied_list():
            var_max_list = {}
            for ld in self.__get_ld_list_from_ied(ied):
                for ln in self.__get_ln_list_from_ld(ld=ld):
                    lntype = self.get_lntype_by_id(ln.get('lnType'))
                    lninst = ied.get('name')+ld.get('inst')+'/'+self.get_ln_name_inst(ln)
                    for do in self.get_do_list_from_lntype(lntype):
                        dotype = self.__get_dotypeobj_by_id(do.get('type'))
                        var_max_list.update(self.var_type_maxvalue_builder(dotype=dotype, name=lninst+'.'+do.get('name'), tempd={}))
                    for k, v in var_max_list.items():
                        print(k, v)

    def get_rcb_list_from_ld(self, ld):
        rc_list=[]
        for rc in ld.LN0.iterchildren(tag='{*}ReportControl'):
            rc_list.append(rc)
        return rc_list



    def get_all_reports_dicts_list_from_rc(self, reportcontrol):
        reports_list = []
        res_dict = {}

        if hasattr(reportcontrol, 'TrgOps'):
            res_dict['dchg'] = bool(reportcontrol.TrgOps.get('dchg') == 'true')
            res_dict['qchg'] = bool(reportcontrol.TrgOps.get('qchg') == 'true')
            if reportcontrol.TrgOps.get('dupd'):
                res_dict['dupd'] = bool(reportcontrol.TrgOps.get('dupd') == 'true')
            res_dict['period'] = bool(reportcontrol.TrgOps.get('period') == 'true')

        if hasattr(reportcontrol, 'OptFields'):
            res_dict['seqNum'] = bool(reportcontrol.OptFields.get('seqNum') == 'true')
            res_dict['timeStamp'] = bool(reportcontrol.OptFields.get('timeStamp') == 'true')
            res_dict['reasonCode'] = bool(reportcontrol.OptFields.get('reasonCode') == 'true')
            res_dict['dataSet'] = bool(reportcontrol.OptFields.get('dataSet') == 'true')
            res_dict['dataRef'] = bool(reportcontrol.OptFields.get('dataRef') == 'true')

        conf_rev = reportcontrol.get('confRev')
        buf = reportcontrol.get('bufTime')
        is_buff = bool(reportcontrol.get('buffered')=='true')
        res_dict['bufTime'] = buf
        res_dict['confRev'] = conf_rev
        res_dict['buffered'] = is_buff
        is_buffered = ('BR' if res_dict['buffered'] else 'RP')
        ldev_parent = reportcontrol.iterancestors(tag='{*}LDevice')
        ied_parent = reportcontrol.iterancestors(tag='{*}IED')
        for ied in ied_parent:
            for ldev in ldev_parent:
                pre_name = ied.get('name')+ldev.get('inst')

        # forks if more than 1 subscriber
        if hasattr(reportcontrol, 'RptEnabled'):
            report_num = int(reportcontrol.RptEnabled.get('max'))
            for i in range(report_num):
                res_dict = {}
                if report_num < 8:
                    rcname = reportcontrol.get('name')+'0'+str(i+1)
                else:
                    rcname = reportcontrol.get('name')+str(i+1)
                res_dict['bufTime'] = buf
                res_dict['confRev'] = conf_rev
                res_dict['buffered'] = is_buff
                res_dict['rptID'] = pre_name+'/LLN0$'+is_buffered+'$'+rcname
                res_dict['CBref'] = pre_name+'/LLN0.'+is_buffered+'.'+rcname
                if hasattr(reportcontrol, 'TrgOps'):
                    res_dict['dchg'] = bool(reportcontrol.TrgOps.get('dchg') == 'true')
                    res_dict['qchg'] = bool(reportcontrol.TrgOps.get('qchg') == 'true')
                    if reportcontrol.TrgOps.get('dupd'):
                        res_dict['dupd'] = bool(reportcontrol.TrgOps.get('dupd') == 'true')
                    res_dict['period'] = bool(reportcontrol.TrgOps.get('period') == 'true')
                if hasattr(reportcontrol, 'OptFields'):
                    res_dict['seqNum'] = bool(reportcontrol.OptFields.get('seqNum') == 'true')
                    res_dict['timeStamp'] = bool(reportcontrol.OptFields.get('timeStamp') == 'true')
                    res_dict['reasonCode'] = bool(reportcontrol.OptFields.get('reasonCode') == 'true')
                    res_dict['dataSet'] = bool(reportcontrol.OptFields.get('dataSet') == 'true')
                    res_dict['dataRef'] = bool(reportcontrol.OptFields.get('dataRef') == 'true')
                reports_list.append(res_dict)
        else:
            rcname = reportcontrol.get('name')+'01'
            res_dict['rptID'] = pre_name +'/LLN0$'+is_buffered+'$'+rcname
            res_dict['CBref'] = pre_name +'/LLN0.'+is_buffered+'.'+rcname
            reports_list.append(res_dict)
        return reports_list



    def trigger_that_var(self, dotype, name, tempd, fc):
        temp_dict = tempd
        [rc_dchg, rc_qchg] = fc
        for da in dotype.iterchildren():
            if not da.get('type') or (da.get('type') and da.get('bType')=='Enum'):
                if da.get('dchg') and da.get('dchg') == 'true':
                    #rc_dchg = da.get('dchg')
                    rc_dchg = (bool(0) if not (da.get('dchg') == 'true') == rc_dchg else bool(1))
                    #rc_dchg = (bool(0) if da.get('dchg') == 'false' else bool(1))
                else:
                    rc_dchg = bool(0)
                if da.get('qchg') and da.get('qchg') == 'true':
                    rc_qchg = (bool(0) if not (da.get('qchg') == 'true') == rc_qchg else bool(1))
                else:
                    rc_qchg = bool(0)
                temp_dict[name+'.'+da.get('name')]=(rc_dchg, rc_qchg)
                [rc_dchg, rc_qchg] = fc
            else:
                self.trigger_that_var(self.get_datatype_by_id(da.get('type')), name+'.'+da.get('name'), temp_dict, fc)
        return temp_dict

# returns a dictionary of Varname : Tuple (data, quality triggers)
    def get_reported_vars(self, iedname, ld, report):
        report_list = self.get_all_reports_dicts_list_from_rc(report)
        for report_dict in report_list:
            triggers = (report_dict['dchg'], report_dict['qchg'])
            ds = self.get_dataset_from_ld_by_name(ld, report.get('datSet'))
            reported_vars = {}
            for fcda in self.get_fcda_list_from_ds(ds):
                ln_name = self.get_ln_name_from_fcda(fcda)
                lntype = self.get_lntype_by_id((self.get_lntype_by_full_ln_name(ld, ln_name)))
                lninst = iedname + ld.get('inst')+'/'+self.get_ln_name_from_fcda(fcda)+'.'
                for do in self.get_do_list_from_lntype(lntype):
                    dotype = self.__get_dotypeobj_by_id(do.get('type'))
                    if do.get('name')==fcda.get('doName'):
                        reported_vars.update(self.trigger_that_var(dotype, name=lninst+do.get('name'), tempd={}, fc=triggers))
        return reported_vars

    # def test_report_control(self, ied_ld_name, clt):
    #     print()
    #     ied = self.get_ied_by_iedld_name(ied_ld_name)
    #     for ld in self.__get_ld_list_from_ied(ied):
    #         for report in self.get_rcb_list_from_ld(ld):
    #             report_list = self.get_all_reports_dicts_list_from_rc(report)
    #             reported_vars = self.get_reported_vars(ied.get('name'), ld, report)
    #             for report_dict in report_list:
    #                 print('Working with \t\t\t :::::::', report_dict['CBref'])
    #                 print(report_dict['CBref'])
    #                 clt.get_rcb(report_dict['CBref'])
    #                 clt.install_handler(report_dict['CBref'], report_dict['rptID'])
    #                 # for k, v in reported_vars.items():
    #                 #    print('\t\tVariables: ')
    #                 #    print(k, v, report_dict['dchg'], report_dict['qchg'])
    #                 clt.trigger_gi(report_dict['CBref'])
    #                 #clt.disable_report()
    #                 clt.destroy_report()
    #                 clt.get_report_enabled()
    #     return True

    # def test_report_control(self, ied_ld_name, clt):
    #     print()
    #     clt.get_rcb('TEMPLATELD0/LLN0.BR.brcbMX0201')
    #     clt.install_handler('TEMPLATELD0/LLN0.BR.brcbMX0201', 'TEMPLATELD0/LLN0$BR$brcbMX0201')
    #     #clt.trigger_gi('TEMPLATELD0/LLN0.BR.brcbMX0201')
    #     #clt.disable_report()
    #     #clt.destroy_report()
    #     time.sleep(3)
    #     clt.triggerReport()
    #     #clt.get_report_enabled()
    #     #clt.destroy_report()
    #     return True
    def shm_client(self, filename):
        client = '/home/ivan/Projects/sas/rattlehead/build/test/tools/test-client'
        connection = 'conn1'
        timeout = str(0)
        cmd = client+' --connection='+connection+' --file='+filename+' --timeout='+timeout +' > /dev/null'
        proc = subprocess.run(cmd, shell = True)

    def test_report_control(self, ied_ld_name, clt):
        print()
        print('getting RCB')
        # clt.get_rcb('TEMPLATELD0/LLN0.BR.brcbMX0101')
        clt.get_rcb('RP2_19LD0/LLN0.BR.brcbMX01')
        clt.enable_report()
        # clt.get_rcb('RP2_19LD0/LLN0.BR.brcbST01')
        # clt.get_report_enabled()
        # clt.install_handler()
        # clt.get_report_enabled()
        # clt.install_handler('TEMPLATELD0/LLN0.BR.brcbST0101', 'TEMPLATELD0/LLN0$BR$brcbST0101')
        # clt.install_handler('TEMPLATELD0/LLN0.BR.brcbMX0101', 'TEMPLATELD0/LLN0$BR$brcbMX0101')
        # clt.install_handler('RP2_19LD0/LLN0.BR.brcbST01', 'RP2_19LD0/LLN0$BR$brcbST01')
        clt.install_handler('RP2_19LD0/LLN0.BR.brcbMX01', 'RP2_19LD0/LLN0$BR$brcbMX01')
        # clt.install_handler('ECISepam80_8/LLN0.BR.brcbMX01', 'ECISepam80_8/LLN0$BR$brcbMX01')
        # input("Waiting...")
        # clt.install_handler()
        # clt.enable_report()
        # clt.get_report_enabled()
        # clt.trigger_gi('TEMPLATELD0/LLN0.BR.brcbMX0201')
        # clt.disable_report()
        # clt.destroy_report()
        print('timer')
        time.sleep(2)
        # clt.triggerReport()
        # clt.get_report_enabled()
        # clt.destroy_report()
        return True

    def get_rc_instances(self):
        for ied in self.get_ied_list():
            for ld in self.__get_ld_list_from_ied(ied):
                for report in self.get_rcb_list_from_ld(ld):
                    report_list = self.get_all_reports_dicts_list_from_rc(report)
                    reported_vars = self.get_reported_vars(ied.get('name'), ld, report)
                    for rd in report_list:
                        print('Report', rd['rptID'], rd['CBref'])
                        print('\t\t\tVars: ')
                        for key, var in reported_vars.items():
                            print(key, var,  rd['dchg'], rd['qchg'])
#                   print(ied.get('name'),ld.get('inst'), report.get('name'))
                   #print(reported_vars)
#                   for report_dict in report_list:
#                       print('Working with \t\t\t :::::::', report_dict['CBref'])
#                       print(report_dict['rptID'])
#                       print('\t\tVariables: ')
#                       for k, v in reported_vars.items():
#                           print(k, v, report_dict['dchg'], report_dict['qchg'])

'''
#############################################################################
'''

if __name__ == "__main__":
    try:
        ip = "192.168.137.34"
        #full_ld = "ECIECI"
        ls = ["/home/ivan/Projects/data/ECI.scd", "/home/ivan/Projects/data/SCD.scd", "/home/ivan/Projects/data/B20.icd" ]
        #ls = ["B20.icd" ]
        #ls = ["SCD.scd" ]
        #ls = ["ECI.scd" ]
        print("*"*100)
        for i in ls:
            scl=SclParser(i)
            scl.get_rc_instances()

            print("*"*100)
    except Exception as e:
        print('Exception: ', str(e) )
