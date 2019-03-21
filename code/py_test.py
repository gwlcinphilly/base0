"""
This is module level testing
"""
__all__ = ['ModuleTest']

import unittest
import py_codeanalyst
from baselibs import get_log

locallog = get_log()  # pylint: disable=C0103

class ModuleTest(unittest.TestCase):
    """Test current modules/libary"""

    def test_codequality(self):
        """test all library in this module"""
        import __init__
        modulelist = __init__.__all__
        for modulename in modulelist:
            codeanalyst_rate = py_codeanalyst.localtest(modulename)
            locallog.debug(f"CodeQuality:{modulename}:: {codeanalyst_rate}")
            self.assertGreater(codeanalyst_rate, 9.0,
                               f"Module name is {modulename}, rate is \
                               {codeanalyst_rate}")

    @unittest.skip(f"skip contant test")
    def test_constant(self):
        """Testing constant define and import"""
        pass

    def test_baselibs_funcs(self):
        """Testing baselibs library functions"""
        import baselibs
        defineresult, testresult = baselibs.localtest_funcs()
        self.assertDictEqual(defineresult,
                             testresult,
                             f"Check the log for detail failed reason")
        return

    def test_baselibs_classes(self):
        """ Testing baselibs library classes"""
        pass

    def test_stringprocess(self):
        """Testing string process library"""
        pass

    def test_stringformat(self):
        """Testing String format library"""
        pass

    def test_network_simpleserver(self):
        import network_simpleserver
        self.assertEqual(network_simpleserver.localtest_funcs(), [True, True],
                         "http server testing done")
if __name__ == "__main__":
    unittest.main(warnings='ignore')
