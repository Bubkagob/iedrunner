import os
import argparse
import sys
import re
current_path=os.path.dirname(os.path.abspath(__file__))
iec_path = os.path.join(current_path, 'iec61850')
client_path = os.path.join(current_path, 'client')
sys.path.append(client_path)
sys.path.append(iec_path)

from client import unit

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



def is_valid_file(parser, arg):
    arg = os.path.abspath(arg)
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
    else:
        print("The file %s does exist" % arg)
        return arg

def inputFileParse():
    parser = argparse.ArgumentParser(prog = 'test')
    parser.add_argument('-f', '--file', type=lambda x: is_valid_file(parser, x), metavar="FILE", default='SCD.scd',  help='Name of xml-like 61850 file for %(prog)s program')
    parser.add_argument('-ip', '--ip', dest='IED', required=True, help='IED\'s IP Address')
    return parser

'''
#############################################################################
#                                  main                                     #
#############################################################################
'''

if __name__ == '__main__':
    parser = inputFileParse()
    filename = parser.parse_args(sys.argv[1:]).file
    try:
        isValidIp = is_ipv4(sys.argv[4])
        if isValidIp:
            print('IP is valid: %s' % sys.argv[4])
            ip = sys.argv[4]
            unit.run_all_tests(filename, ip) # <-------------Tests runs
        else:
            print('IP is invalid: %s' % sys.argv[4])
    except ValueError:
        print('IP is invalid: %s' % sys.argv[4])
    except:
        print('Invalid usage : %s  ip' % sys.argv[4])
