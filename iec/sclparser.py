from lxml import etree, objectify

class SclParser:
    def __init__(self, scd_file):
        root = objectify.parse(scd_file)
        self.__FILENAME = scd_file
        self.__root = root.getroot()
        self.__ddt = self.__root.DataTypeTemplates

    #lxml list
    def __get_subnet_list(self):
        sn_list = []
        try:
            for sn in self.__root.Communication.iterchildren():
                sn_list.append(sn)
            return sn_list
        except:
            return sn_list

    #lxml list
    def get_ap_list(self):
        ap_list = []
        for sn in self.__get_subnet_list():
            for capp in sn.iterchildren():
                ap_list.append(capp)
        return ap_list

    #object ied list
    def get_ied_list(self):
        ied_list=[]
        for ied in self.__root.IED:
            ied_list.append(ied)
        return ied_list

    #object LD list
    def __get_ld_list_from_ied(self, ied):
        ld_list = []
        gen = (device for device in ied.AccessPoint.Server.iterchildren() if device.get('inst'))
        for device in gen:
            ld_list.append(device)
        return ld_list

    def get_ld_list_from_file(self):
        ld_list = []
        for ied in self.get_ied_list():
            for ld in self.__get_ld_list_from_ied(ied):
                ld_list.append(ld)
        return ld_list


    #IEDname list IED name + inst
    def get_ied_ld_names(self):
        iedname_list = []
        for ied in self.get_ied_list():
            for ld in self.__get_ld_list_from_ied(ied):
                iedname_list.append(ied.get('name')+ld.get('inst'))
        return iedname_list

    #IED_LDname list by IED_LD name
    def get_ied_ld_names_by_ied(self, ied):
        iedname_list = []
        for ld in self.__get_ld_list_from_ied(ied):
            iedname_list.append(ied.get('name')+ld.get('inst'))
        return iedname_list

    #all of AP ip list from Communication block
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

    def get_names_from_datatype(self, dotype):
        da_list = []
        for da in dotype.iterchildren():
            da_list.append(da.get('name'))
        return da_list

    def check_dai(self, dai, dotype):
        if dai.get('name') in self.get_names_from_datatype(dotype):
            return True
        else:
            print("Failed with DAI ckecking === > ", dai.get('name'), "on line", dai.sourceline)
            return False


    def get_da_from_dotype_by_name(self, dotype, daname):
        gen = (datype for datype in dotype.iterchildren() if datype.get('type') and datype.get('name')==daname)
        for el in gen:
            print(el.get('type'))

    def check_sdi(self, sdi, dotype):
        if sdi.get('name') in self.get_names_from_datatype(dotype):
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
            if full_lnname == self.__get_ln_name_inst(lnode):
                return lnode.get('lnType')

    #Lnode full name with instance number
    def __get_ln_name_inst(self, lnode):
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
            res_list.append(self.__get_ln_name_inst(lnode))
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
        for lntype in self.__ddt.LNodeType:
            print(lntype.get('id'))

    #print all DOType names from file
    def get_dotype_list_from_file(self):
        for do_type in self.__ddt.DOType:
            print(do_type.get('id'))

    #print all DAType names from file
    def get_datype_list_from_file(self):
        for do_type in self.__ddt.DAType:
            print(do_type.get('id'))

    def get_dotype_from_lntype_by_name(self, lntype, doiname):
        gen = (do for do in lntype.DO if do.get('name')==doiname)
        for el in gen:
            return self.__get_dotypeobj_by_id(el.get('type'))

    def __get_dotypeobj_by_id(self, dotypeid):
        gen = (dotype for dotype in self.__ddt.DOType if dotype.get('id')==dotypeid)
        for dotype in gen:
            #print("вернули DOType:\t\t\t\t\t",dotype.get('id'))
            return dotype

    def get_dotypelist_from_lntype_by_lnid(self, lnid):
        do_list = []
        gen = (lntype for lntype in self.__ddt.LNodeType if lntype.get('id')==lnid)
        for lnodetype in gen:
            #print("вернули LNodeType:\t\t\t\t",lnodetype.get('id'))
            for do in lnodetype.iterchildren():
                do_list.append(do.get('name'))
        return do_list


    def get_lntype_by_id(self, idtype):
        gen = (lntype for lntype in self.__ddt.LNodeType if lntype.get('id')==idtype)
        for lnodetype in gen:
            #print("вернули LNodeType:\t\t\t\t",lnodetype.get('id'))
            return lnodetype

    def get_ds_list_from_ld(self, ld):
        ds_list=[]
        for ds in ld.LN0.iterchildren(tag='{*}DataSet'):
            ds_list.append(ds)
        return ds_list

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

    def get_fcda_list_from_ds(self, ds):
        fcda_list = []
        for fcda in ds.iterchildren(tag='{*}FCDA'):
            fcda_list.append(fcda)
        return fcda_list

    def get_ln_name_from_fcda(self, fcda):
        if fcda.get('prefix'):
            return (fcda.get('prefix')+fcda.get('lnClass')+fcda.get('lnInst'))
        else:
            if fcda.get('lnInst'):
                return (fcda.get('lnClass')+fcda.get('lnInst'))
            else:
                return (fcda.get('lnClass'))

    # ========= 1 test Присутствуют все типы, используемые в ied
    def is_all_types_is_ok(self):
        for ied in self.get_ied_list():
            for ld in self.__get_ld_list_from_ied(ied):
                for ln in self.__get_ln_list_from_ld(ld):
                    lnt = self.get_lntype_by_id(ln.get('lnType'))
                    for doi in self.__get_doi_list_from_ln(ln):
                        dotype_list = self.get_dotypelist_from_lntype_by_lnid(ln.get('lnType'))
                        dotype = self.get_dotype_from_lntype_by_name(lnt, doi.get('name'))
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

    # ========= 2 IED Присутствуют обязательные параметры
    def is_all_attributes_in_ied_is_ok(self):
        req = ['name', 'type', 'manufacturer', 'configVersion']
        for ied in self.get_ied_list():
            if not set(req) <= set(ied.keys()):
                print("Not enough attributes in IED on line", ied.sourceline)
                return False
        return True

    # ========= 3 LN Присутствуют обязательные параметры
    def is_all_attributes_in_ln_is_ok(self):
        req = ['inst', 'lnClass', 'lnType']
        for ln in self.get_ln_list_from_file():
            if not set(req) <= set(ln.keys()) :
                print("Not enough attributes in LN on line", ln.sourceline)
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
                for fcda in self.get_fcda_list_from_ds(ds):
                    if not set(req_fcda) <= set(fcda.keys()) :
                        print("Not enough attributes in FCDA on line", fcda.sourceline)
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
        for ld in self.get_ld_list_from_file():
            for rc in self.get_rc_list_from_ld(ld):
                if not set(req) <= set(rc.keys()) :
                    print("Not enough attributes in RC on line", rc.sourceline)
                    return False
        return True

    # ========= 7 в RC Присутствуют ссылки на имеющиеся dset
    def is_all_report_control_linked(self):
        for ld in self.get_ld_list_from_file():
            for rc in self.get_rc_list_from_ld(ld):
                if not rc.get('datSet') in self.get_dsnames_list_from_ld(ld):
                    print("Unlinked ReportControl Block on line", rc.sourceline)
                    return False
        return True


    # ========= IECTestCase # test Присутствуют обязательные параметры
    def is_structure_equal(self, ied_ld_name, clt):
        ied = self.get_ied_by_iedld_name(ied_ld_name)
        ied_ld_list_from_file = self.get_ied_ld_names_by_ied(ied)
        #print(ied_ld_list_from_file)
        for ld in clt.get_ld_list():
            ld_server_name = clt.get_name_of(ld)
            #print("Check LD [SRV]", ld_server_name)
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

    def test_ex(self):
        ln_list=[]
        for ied in self.get_ied_list():
            for ld in self.__get_ld_list_from_ied(ied):
                for ln in self.__get_ln_list_from_ld(ld):
                    ln_list.append(ied.get('name')+ld.get('inst')+'/'+ln.get("lnType"))
        print(ln_list)
        return ln_list

'''
#############################################################################
'''

if __name__ == "__main__":
    try:
        ip = "192.168.137.34"
        full_ld = "ECIECI"
        ls = ["ECI.scd", "SCD.scd", "B20.icd" ]
        print("*"*100)
        for i in ls:
            scl=SclParser(i)
            scl.get_ied_by_iedld_name('ECISepam20_7')
            print("*"*100)
    except Exception as e:
        print('Exception: ', str(e) )
