import sip
sip.setapi('QString', 2)

import unittest

class TestCase(unittest.TestCase):
    def setUp(self):
        super(TestCase, self).setUp()
        from re_eat.models import initialize_testing_sql
        initialize_testing_sql()

    def tearDown(self):
        super(TestCase, self).tearDown()
        from re_eat.models import Session
        Session.remove()

