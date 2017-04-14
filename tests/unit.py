import unittest
from iec import client, sclparser

class IECTestCase(unittest.TestCase):
    def __init__(self,  testname, filename, ip, iedname):
        super(IECTestCase, self).__init__(testname)
        self.__FILENAME = filename
        self.__IP = ip
        self.__IEDNAME = iedname
        self.clt = client.iecClient(self.__IP)
# '''
# Связь с сервером? Если нет --> Отмена теста
# '''
        try:
            self.assertTrue(self.clt.getConnectionState())
        except Exception:
            self.skipTest("Connection error")
#
# Имеется ли ied из аргументов в сервере. Если нет --> Отмена теста
#
        try:
            self.assertTrue(self.__IEDNAME in self.clt.getIEDnameList())
        except Exception:
            self.skipTest("IED not in Server")
# '''
# Имеется ли ied в списке ied+ldinst в файле. Если нет --> Отмена теста
# '''
        try:
            self.assertTrue(self.__IEDNAME in sclparser.getIED_LDnameList(self.__FILENAME))
        except Exception:
            self.skipTest("LD instance not in File")
    def setUp(self):
        pass

    def tearDown(self):
        self.clt.stop()


    #connect state btwn client - server
    def test_connection(self):
        self.assertTrue(self.clt.getConnectionState())

    def test_print(self):
        self.assertTrue(True)

    @unittest.skipIf(not test_connection, "Reason: connection_test Failed")
    def test_skip(self):
        self.assertTrue(True)


def run_all_tests(filename, ip, iedname):
    suite = unittest.TestSuite()
    suite.addTest(IECTestCase("test_connection", filename, ip, iedname))
    suite.addTest(IECTestCase("test_print", filename, ip, iedname))
    suite.addTest(IECTestCase("test_skip", filename, ip, iedname))
    unittest.TextTestRunner(verbosity=2).run(suite)
