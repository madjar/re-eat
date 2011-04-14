# -*- coding: utf-8 -*-

import sip
sip.setapi('QString', 2)

import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from re_eat.models import initialize_testing_sql, Session, Tag, Recipe
from re_eat.tags import TagsWidget

def main():
    initialize_testing_sql()

    Session.add(Recipe(u"Carbo"))
    Session.add_all(Tag(t) for t in [u'lourd', u'pâtes', u'hiver'])


    app = QApplication(sys.argv)

    w = TagsWidget()
    w.show()

    app.exec_()
    sys.exit()

