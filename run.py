import os
import argparse
import sys
import re
from tests import *

def is_ipv4(parser, arg):
	match = re.match("^(\d{0,3})\.(\d{0,3})\.(\d{0,3})\.(\d{0,3})$", arg)
	if not match:
		parser.error("The IP %s is incorrect!" % arg)
	quad = []
	for number in match.groups():
		quad.append(int(number))
	if quad[0] < 1:
		parser.error("The IP %s is incorrect!" % arg)
	for number in quad:
		if number > 255 or number < 0:
			parser.error("The IP %s is incorrect!" % arg)
	return arg



def is_valid_file(parser, arg):
    arg = os.path.abspath(arg)
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
    else:
        return arg

def inputFileParse():
    parser = argparse.ArgumentParser(prog = os.path.basename(__file__))
    parser.add_argument('-f', '--file', dest='filename', type=lambda x: is_valid_file(parser, x), metavar="FILE", default='SCD.scd',  help='Name of xml-like 61850 file for %(prog)s program')
    parser.add_argument('-ip', '--ip', dest='ip', type=lambda x: is_ipv4(parser, x), required=True, help='Server ip')
    parser.add_argument('-ied', '--ied', dest='iedname', required=True, help='full IED name')
    return parser

'''
#############################################################################
#                                  main                                     #
#############################################################################
'''

if __name__ == '__main__':

    [filename, ip, iedname] = inputFileParse().parse_args().filename, inputFileParse().parse_args().ip, inputFileParse().parse_args().iedname,
    try:
        unit.run_all_tests(filename, ip, iedname) # <-------------Tests runs
    except Exception as e:
        print('Exception: ', str(e))
