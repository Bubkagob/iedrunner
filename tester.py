import http.client
import time
import xml.dom.minidom
import random
from sim import control_server
import json
from optparse import OptionParser
parser = OptionParser()
parser.add_option("-c", "--config",
                  dest="config_file",
                  type="string",
                  help="Config file name",
                  metavar="FILE"
                  )
(options, args) = parser.parse_args()
if options.config_file is None:
    raise Exception("Parameter '-c' not specified. Set it to config file name")

g_Config = json.loads(open(options.config_file).read())


def ReadHttp(con, requestStr):
    con.request("GET", requestStr)
    response = con.getresponse()
    if response.status != 200:
        raise Exception("Bad web response: "+str(response.status) +
                        " "+response.reason+" on "+requestStr)
    xmlText = response.read()
    dom = xml.dom.minidom.parseString(xmlText)
    return dom


def GetXmlNodeText(node):
    rs = []
    for ch in node.childNodes:
        if ch.nodeType == node.TEXT_NODE:
            rs.append(ch.data)
    return "".join(rs)


def GetXmlValue(dom, path):
    cnd = dom.documentElement
    for p in path.split("/"):
        cnds = [c for c in cnd.childNodes if c.nodeName == p]
        if len(cnds) == 0:
            raise Exception("Xml node '" + path + "' not found")
        cnd = cnds[0]
    return GetXmlNodeText(cnd)


class HttpTag:
    def __init__(self, con, longName):
        self.HttpCon = con
        self.LongName = longName
        dom = ReadHttp(self.HttpCon, "/find?name=" + longName)
        self.Id = int(GetXmlValue(dom, "id"))
        print('Id from class', self.Id)

    def Read(self):
        dom = ReadHttp(self.HttpCon, "/get?id=" + str(self.Id))
        StrValue = GetXmlValue(dom, 'tag/value')
        TStampUTC = GetXmlValue(dom, "tag/timeUTC")
        Quality = int(GetXmlValue(dom, "tag/quality"))
        type = GetXmlValue(dom, "tag/type")
        value = None
        if type == "bool":
            value = StrValue == "1"
        elif type == "i32":
            value = int(StrValue)
        elif type == "ui32":
            value = int(StrValue)
        elif type == "i64":
            value = int(StrValue)
        elif type == "ui64":
            value = int(StrValue)
        elif type == "f32":
            value = float(StrValue)
        elif type == "f64":
            value = float(StrValue)
        elif type == "str":
            value = float(StrValue)
        else:
            raise Exception("Unknown value type: '{}'".format(type))
        print("Tag Value = '{}' quality = '{}' tstamp = '{}'".format(value,
                                                                     Quality,
                                                                     TStampUTC))
        return(value, Quality, TStampUTC)


def produceValue(d):
    val_min = d.get('min', 0)
    val_max = d.get('max', 255)
    if d['type'] == 'int':
        return random.randint(val_min, val_max)
    else:
        return random.uniform(val_min, val_max)

# ----------------------------
g_ContinueRunning = True
try:
    # create connection to vc web
    web_services_con = http.client.HTTPConnection(
        g_Config['web_services']['ip_addr'],
        g_Config['web_services']['tcp_port']
        )
    sim_control_con = control_server.RemoteConnection()
    sleep_time_ms = g_Config['params']['sleeps_ms']
    # dict with http tags
    http_tags = {}
    for value in g_Config['tested_values']:
        id = value['id']
        print("Id is ", id)
        db_name = value['web_services']['db_name']
        print('Db name', db_name)
        http_tag = HttpTag(web_services_con, db_name)
        http_tags[id] = http_tag

    while g_ContinueRunning:
        values_map = {}
        # Step 1. Generate rnd
        for value in g_Config['tested_values']:
            id = value['id']
            new_value = produceValue(value['sim']['value'])
            print(new_value)
            values_map[id] = new_value
            sim_control_con.Modify(value['sim']['dev_name'],
                                   value['sim']['tag_name'],
                                   new_value)
        print(values_map)
        time.sleep(sleep_time_ms)
        for value in g_Config['tested_values']:
            id = value['id']
            http_tag = http_tags[id]
            vqt = http_tag.Read()
            if vqt[0] != values_map[id]:
                print("Not eq!")

        for value in g_Config['tested_values']:
            id = value['id']
            tag = http_tags[id]
            readed_tag = tag.Read()
            print(readed_tag)


except Exception as e:
    print('Something goes wrong', str(e))
