import unittest
import lxml
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

    def test_types(self):
        self.assertTrue(self.scl.is_all_types_is_ok())

    def test_ied_attributes(self):
        self.assertTrue(self.scl.is_all_attributes_in_ied_is_ok())

    def test_ln_attributes(self):
        self.assertTrue(self.scl.is_all_attributes_in_ln_is_ok())

    def test_ds_attributes(self):
        self.assertTrue(self.scl.is_all_attributes_in_ds_is_ok())

    def test_ds_refs(self):
        self.assertTrue(self.scl.is_all_ds_targets_is_ok())

    def test_rc_attributes(self):
        self.assertTrue(self.scl.is_all_attributes_in_rc_is_ok())

    def test_rc_refs(self):
        self.assertTrue(self.scl.is_all_report_control_linked())

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
            self.skipTest("Connection error")
#
# Имеется ли ied из аргументов в сервере. Если нет --> Отмена теста
#
        try:
            self.assertTrue(self.__IEDLDNAME in self.clt.get_ied_ld_names())
        except Exception:
            self.skipTest("IED not in Server")
# '''
# Имеется ли ied в списке ied+ldinst в файле. Если нет --> Отмена теста
# '''
        try:
            self.assertTrue(self.__IEDLDNAME in self.scl.get_ied_ld_names())
        except Exception:
            self.skipTest("LD instance not in File")

    def tearDown(self):
        self.clt.stop()


    #connect state btwn client - server
    def test_connection(self):
        self.assertTrue(self.clt.get_connection_state())

    @unittest.skipIf(not test_connection, "Reason: connection_test Failed")
    def test_structure_check_in_server(self):
        self.assertTrue(self.scl.is_structure_equal(self.__IEDLDNAME, self.clt))


    @unittest.skipIf(not test_connection, "Reason: connection_test Failed")
    def test_skip(self):
        self.assertTrue(True)


def run_scl_types_tests(filename):
    suite = unittest.TestSuite()
    suite.addTest(SCLTestCase("test_types", filename))
    suite.addTest(SCLTestCase("test_ied_attributes", filename))
    suite.addTest(SCLTestCase("test_ln_attributes", filename))
    suite.addTest(SCLTestCase("test_ds_attributes", filename))
    suite.addTest(SCLTestCase("test_ds_refs", filename))
    suite.addTest(SCLTestCase("test_rc_attributes", filename))
    suite.addTest(SCLTestCase("test_rc_refs", filename))
    unittest.TextTestRunner(verbosity=2).run(suite)

def run_all_tests(filename, ip, ied_ld_name):
    suite = unittest.TestSuite()
    suite.addTest(IECTestCase("test_connection", filename, ip, ied_ld_name))
    suite.addTest(IECTestCase("test_structure_check_in_server", filename, ip, ied_ld_name))
    suite.addTest(IECTestCase("test_skip", filename, ip, ied_ld_name))
    unittest.TextTestRunner(verbosity=2).run(suite)
