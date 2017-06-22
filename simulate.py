#coding=utf-8
from sim import modbus, simlib, control_server, nzif

# Parse command line
import json
from optparse import OptionParser
parser = OptionParser()
parser.add_option(
                "-c",
                "--config",
                dest="config_file",
                type="string",
                help="Config file name",
                metavar="FILE"
)

(options, args) = parser.parse_args()

if options.config_file is None:
	raise Exception("Parameter '-c' not specified. Set it to config file name")

# Load and parse config
g_Config = json.loads(open(options.config_file).read())

iface = g_Config['iface']

# Create NZIF device servers
if 'nzif_servers' in g_Config:
	for server_info in g_Config['nzif_servers']:
		srv_inst = NZIFServer()
		simblib.listen(iface, server_info['tcp_port'], srv_inst)

		for device_info in server_info['devices']:
			dev_inst = NZIFDevice()
			dev_inst.Password = device_info['pwd']
			RegisterControlledObject (device_info['name'], dev_inst)
			srv_inst.Slaves[ device_info['slave_nb'] ] = dev_inst

			print ("Registered NZIF device " + device_info['name'])

# Create Modbus TCP device servers
if 'mb_servers' in g_Config:
	for server_info in g_Config['mb_servers']:
		srv_inst = modbus.MbTcpServer()
		simlib.listen(iface, server_info['tcp_port'], srv_inst)

		for device_info in server_info['devices']:
			dev_inst = modbus.SimpleMbDevice()
			simlib.RegisterControlledObject (device_info['name'], dev_inst)
			srv_inst.Slaves[ device_info['slave_nb'] ] = dev_inst

			print ("Registered Modbus device " + device_info['name'])


control_server.EnableRemoteControl ()
simlib.simulate ()
