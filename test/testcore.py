import unittest


def tests_from_modules(modnames):
    return [unittest.findTestCases(__import__(modname, fromlist=['*']))
             for modname in modnames]


def get_test_runner(runner=unittest.TextTestRunner()):
    # use xmlrunner if available; otherwise, fall back to text runner
    try:
        import xmlrunner
        runner = xmlrunner.XMLTestRunner(output='test-results')
    except ImportError:
        pass
    return runner


def main(testRunner=None, *args, **kwargs):
    if testRunner is None:
        testRunner = get_test_runner()
    unittest.main(testRunner=testRunner, *args, **kwargs)
