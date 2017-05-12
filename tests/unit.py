import sys
import unittest
import lxml
import time
from iec import client, sclparser


class SCLTestCase(unittest.TestCase):
    def __init__(self, testname, filename):
        super(SCLTestCase, self).__init__(testname)
        self.__FILENAME = filename
        self.scl = sclparser.SclParser(self.__FILENAME)

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_lnodetypes(self):
        self.assertTrue(self.scl.is_lnode_types_ok())

    def test_dotypes(self):
        self.assertTrue(self.scl.is_do_types_ok())

    def test_datypes(self):
        self.assertTrue(self.scl.is_da_types_ok())

    def test_enumtypes(self):
        self.assertTrue(self.scl.is_enum_types_ok())

    def test_ied_attributes(self):
        self.assertTrue(self.scl.is_all_attributes_in_ied_is_ok())

    def test_ln_attributes(self):
        self.assertTrue(self.scl.is_all_attributes_in_ln_is_ok())

    def test_do_attributes(self):
        self.assertTrue(self.scl.is_all_attributes_in_do_is_ok())

    def test_ds_attributes(self):
        self.assertTrue(self.scl.is_all_attributes_in_ds_is_ok())

    def test_ds_refs(self):
        self.assertTrue(self.scl.is_all_ds_targets_is_ok())

    def test_rc_attributes(self):
        self.assertTrue(self.scl.is_all_attributes_in_rc_is_ok())

    def test_rc_refs(self):
        self.assertTrue(self.scl.is_all_report_control_linked())

    def test_types(self):
        self.assertTrue(self.scl.is_all_types_is_ok())

    def test_types_v2(self):
        self.assertTrue(self.scl.is_all_params_in())

class IECTestCase(unittest.TestCase):
    def __init__(self,  testname, filename, ip, ied_ld_name):
        super(IECTestCase, self).__init__(testname)
        self.__FILENAME = filename
        self.__IP = ip
        self.__IEDLDNAME = ied_ld_name


    def setUp(self):
        self.clt = client.IecClient(self.__IP)
        self.scl = sclparser.SclParser(self.__FILENAME)
# '''
# Связь с сервером? Если нет --> Отмена теста
# '''
        try:
            self.assertTrue(self.clt.get_connection_state())
        except Exception:
            self.clt.stop()
            self.skipTest("Reason: Connection error")
#
# Имеется ли ied из аргументов в сервере. Если нет --> Отмена теста
#
        try:
            self.assertTrue(self.__IEDLDNAME in self.clt.get_ied_ld_names())
        except Exception:
            self.clt.stop()
            self.skipTest("Reason: IED not in Server")
# '''
# Имеется ли ied в списке ied+ldinst в файле. Если нет --> Отмена теста
# '''
        try:
            self.assertTrue(self.__IEDLDNAME in self.scl.get_ied_ld_names())
        except Exception:
            self.skipTest("Reason: LD instance not in File")

    def tearDown(self):
        self.clt.stop()


    #connect state btwn client - server
    def test_connection(self):
        self.assertTrue(self.clt.get_connection_state())

    @unittest.skipIf(not test_connection, "Reason: connection_test Failed")
    def test_structure_check_in_server(self):
        self.assertTrue(self.scl.is_structure_equal(self.__IEDLDNAME, self.clt))


    @unittest.skipIf(not test_connection, "Reason: connection_test Failed")
    def test_rcb_instance_name(self):
        self.assertTrue(self.scl.is_rc_names_correct_in_server(self.__IEDLDNAME, self.clt))

    @unittest.skipIf(not test_connection, "Reason: connection_test Failed")
    def test_rcb_attributes(self):
        self.assertTrue(self.scl.test_rc_attributes_ok_in_server(self.__IEDLDNAME, self.clt))

    @unittest.skipIf(not test_connection, "Reason: connection_test Failed")
    def test_node_variable_fc(self):
        self.assertTrue(self.scl.test_lnode_fc_parameters_is_ok(self.__IEDLDNAME, self.clt))

    @unittest.skipIf(not test_connection, "Reason: connection_test Failed")
    def test_node_variable_btype(self):
        self.assertTrue(self.scl.test_lnode_btype_parameters_is_ok(self.__IEDLDNAME, self.clt))

    @unittest.skipIf(not test_connection, "Reason: connection_test Failed")
    def test_var_flow(self):
        self.assertTrue(self.scl.test_var_storm(self.__IEDLDNAME, self.clt))

def run_all_tests(filename, ip, ied_ld_name):
    #test_suite for file tester
    suite = unittest.TestSuite()
    suite.addTest(SCLTestCase("test_lnodetypes", filename))
    suite.addTest(SCLTestCase("test_dotypes", filename))
    suite.addTest(SCLTestCase("test_datypes", filename))
    suite.addTest(SCLTestCase("test_enumtypes", filename))
    suite.addTest(SCLTestCase("test_ied_attributes", filename))
    suite.addTest(SCLTestCase("test_ln_attributes", filename))
    suite.addTest(SCLTestCase("test_do_attributes", filename))
    suite.addTest(SCLTestCase("test_ds_attributes", filename))
    suite.addTest(SCLTestCase("test_ds_refs", filename))
    suite.addTest(SCLTestCase("test_rc_attributes", filename))
    suite.addTest(SCLTestCase("test_rc_refs", filename))
    suite.addTest(SCLTestCase("test_types", filename))
    suite.addTest(SCLTestCase("test_types_v2", filename))
    runnerSCL = unittest.TextTestRunner(verbosity=2)
    resultSCL = runnerSCL.run(suite)
    status_one = len(resultSCL.failures) + len(resultSCL.errors) + len(resultSCL.skipped)

    #test suite for client-server
    suiteIEC = unittest.TestSuite()
    suiteIEC.addTest(IECTestCase("test_connection", filename, ip, ied_ld_name))
    suiteIEC.addTest(IECTestCase("test_structure_check_in_server", filename, ip, ied_ld_name))
    suiteIEC.addTest(IECTestCase("test_rcb_instance_name", filename, ip, ied_ld_name))
    suiteIEC.addTest(IECTestCase("test_rcb_attributes", filename, ip, ied_ld_name))
    suiteIEC.addTest(IECTestCase("test_node_variable_fc", filename, ip, ied_ld_name))
    suiteIEC.addTest(IECTestCase("test_node_variable_btype", filename, ip, ied_ld_name))
    suiteIEC.addTest(IECTestCase("test_var_flow", filename, ip, ied_ld_name))
    runnerIEC = unittest.TextTestRunner(verbosity=2)
    resultIEC = runnerIEC.run(suiteIEC)
    status_two = len(resultIEC.failures) + len(resultIEC.errors) + len(resultIEC.skipped)
    #exit with status code
    sys.exit(status_one+status_two)
    sys.exit(status_two)
