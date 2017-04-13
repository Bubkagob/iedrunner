import unittest
import os
import sys
from tests import cases

class IECTestCase(unittest.TestCase):
    def __init__(self, testname, filename, ip):
        super(IECTestCase, self).__init__(testname)
        self.FILENAME = filename
        self.IP = ip

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_IP_is_in_file(self):
        print('\ntest IP is in file?')
        self.assertTrue(cases.isIp_in_file(filename = self.FILENAME, ied_ip=self.IP))
        print('Success')

    def test_Connect(self):
        print('\ntest Connection to IED')
        self.assertTrue(cases.isConnect(ied_ip=self.IP))
        print('Success')


    def test_Validate_LNodes(self):
        print('\nvalidate Logical Nodes in IED')
        self.assertTrue(cases.isLNodesEqual(filename = self.FILENAME, ied_ip=self.IP))
        print('Success')



def run_all_tests(filename, ip):
    suite = unittest.TestSuite()
    suite.addTest(IECTestCase("test_IP_is_in_file", filename, ip))
    suite.addTest(IECTestCase("test_Connect", filename, ip))
    suite.addTest(IECTestCase("test_Validate_LNodes", filename, ip))
    unittest.TextTestRunner().run(suite)
