import unittest
from src.main import hello_world

class TestMain(unittest.TestCase):
    def test_hello_world(self):
        with self.assertLogs(level='INFO') as log:
            hello_world()
        self.assertIn('Hello, World!', log.output[0])