# -*- coding: utf-8 -*-

import sip
from re_eat.tests.test_recipes import load_some_tags

sip.setapi('QString', 2)

import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from re_eat.models import initialize_testing_sql, Session, Tag, Recipe
from re_eat.tags import TagsWidget
from re_eat.recipes import RecipesWidget

def main():
    initialize_testing_sql()

    load_some_tags()

    app = QApplication(sys.argv)

    l = QVBoxLayout()
    w = QWidget()
    w.setLayout(l)

    rw = RecipesWidget()
    tw = TagsWidget()

    tw.tagsChanged.connect(rw.reload)

    l.addWidget(rw)
    l.addWidget(tw)

    w.show()

    app.exec_()
    sys.exit()

