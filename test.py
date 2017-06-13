import sys
import unittest
import lxml
from iec import client, sclparser

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

    # connect state btwn client - server
    def test_connection(self):
        self.assertTrue(self.clt.get_connection_state())

    @unittest.skipIf(not test_connection, "Reason: connection_test Failed")
    def test_structure_check_in_server(self):
        self.assertTrue(self.scl.is_structure_equal(self.__IEDLDNAME, self.clt))

    @unittest.skipIf(not test_connection, "Reason: connection_test Failed")
    def test_reports(self):
        self.assertTrue(self.scl.test_report_control(self.__IEDLDNAME, self.clt))


def run_all_tests():
    filename = '/home/ivan/Projects/data/SCD.scd'
    # filename = '/home/ivan/Projects/data/B20.icd'
    ip = '10.151.42.125'
    # ip = '127.0.0.1'
    # ied_ld_name = 'TEMPLATELD0'
    ied_ld_name = 'RP2_19LD0'
    suiteIEC = unittest.TestSuite()
    suiteIEC.addTest(IECTestCase("test_reports", filename, ip, ied_ld_name))
    runnerIEC = unittest.TextTestRunner(verbosity=2)
    resultIEC = runnerIEC.run(suiteIEC)
    # status_two = len(resultIEC.failures) + len(resultIEC.errors) + len(resultIEC.skipped)
    # exit with status code
    # sys.exit(status_one+status_two)
    # sys.exit(status_two)
    sys.exit()

if __name__ == '__main__':
    run_all_tests()
