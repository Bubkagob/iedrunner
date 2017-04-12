import os
import argparse
import sys
import re
import traceback
current_path=os.path.dirname(os.path.abspath(__file__))
iec_path = os.path.join(current_path, 'iec61850')
client_path = os.path.join(current_path, 'client')
sys.path.append(client_path)
sys.path.append(iec_path)
from deviceparser import run_client

def is_ipv4(ip):
	match = re.match("^(\d{0,3})\.(\d{0,3})\.(\d{0,3})\.(\d{0,3})$", ip)
	if not match:
		return False
	quad = []
	for number in match.groups():
		quad.append(int(number))
	if quad[0] < 1:
		return False
	for number in quad:
		if number > 255 or number < 0:
			return False
	return True

def inputFileParse():
    parser = argparse.ArgumentParser(prog = 'test')
    parser.add_argument('-ip', '--ip', dest='IP', required=True, help='IED\'s IP Address')
    parser.add_argument('-type', '--type', dest='DT', required=True, help='type DA')
    parser.add_argument('-var', '--var', dest='VAR', required=True, help='variable name')
    return parser



if __name__ == '__main__':
    parser = inputFileParse()
    result = parser.parse_args(sys.argv[1:])
    isValidIp = is_ipv4(result.IP)
    if isValidIp:
        print('IP is valid: %s' % result.IP)
        ip = result.IP
        if(result.DT in 'fbtq'):
            dt = result.DT
            var = result.VAR
            run_client(ip, dt, var)
        else:
            print(result.DT, "isn't correct type")
    else:
        print('IP is invalid: %s' % result.IED)





#run_client()

#
# if __name__ == "__main__":
#     try:
#     	run_client()
#
#     except:
#     	print ("Error :")
#     	traceback.print_exc(file=sys.stdout)
