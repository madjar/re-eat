from re_eat.tests.common import get_app

import unittest
import datetime
from PyQt4.QtGui import QDialogButtonBox
from re_eat.daterange import DateRangeDialog

class DateRangeDialogTestCase(unittest.TestCase):
    def setUp(self):
        super(DateRangeDialogTestCase, self).setUp()
        self.app = get_app()

    def test_invalid_range(self):
        drd = DateRangeDialog()
        drd._fro.setDate(datetime.date.today())
        drd._to.setDate(datetime.date.today()
                            + datetime.timedelta(-2))

        self.assertFalse(drd.buttons.button(QDialogButtonBox.Ok).isEnabled())

    def test_fro_and_to(self):
        fro_val = datetime.date.today()
        to_val = datetime.date.today() + datetime.timedelta(-2)
        drd = DateRangeDialog()
        drd._fro.setDate(fro_val)
        drd._to.setDate(to_val)

        self.assertEqual(drd.fro, fro_val)
        self.assertEqual(drd.to, to_val)