import unittest
import sys
import os

# Add the parent directory to the system path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_suite():
    """Define which test modules to run"""
    test_modules = [
        'tests.test_web_scraper',
        'tests.test_market_data',
        'tests.test_analyzer'
    ]
    
    suite = unittest.TestSuite()
    
    for test_module in test_modules:
        try:
            # Load the module tests
            loaded_tests = unittest.TestLoader().loadTestsFromName(test_module)
            suite.addTests(loaded_tests)
        except Exception as e:
            print(f"Error loading test module {test_module}: {str(e)}")
    
    return suite

if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    test_suite = test_suite()
    runner.run(test_suite)
