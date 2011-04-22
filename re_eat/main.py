# -*- coding: utf-8 -*-

import sip
sip.setapi('QString', 2)
sip.setapi('QDate', 2)

import sys
import datetime
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from re_eat.models import initialize_testing_sql, Session, Tag, Recipe, Meal
from re_eat.meals import PlanningWidget
from re_eat.tags import TagsWidget
from re_eat.recipes import RecipesWidget

from re_eat.tests.test_recipes import load_some_tags


class ReEatWidget(QSplitter):
    def __init__(self):
        super(ReEatWidget, self).__init__(Qt.Horizontal)

        left = QSplitter(Qt.Vertical)
        rw = RecipesWidget()
        tw = TagsWidget()
        tw.tagsChanged.connect(rw.reload)
        left.addWidget(rw)
        left.addWidget(tw)

        self.addWidget(left)

        right = PlanningWidget(datetime.date.today(),
                       datetime.date.today()+datetime.timedelta(4))
        #TODO
        self.addWidget(right)

def main():
    initialize_testing_sql()

    load_some_tags()

    app = QApplication(sys.argv)

    m1 = Meal(datetime.date.today(), 0, [Recipe('carbo')])
    m2 = Meal(datetime.date.today()+datetime.timedelta(2), 0, [Recipe('lala')])
    m3 = Meal(datetime.date.today()+datetime.timedelta(3), 1, [Recipe('viande')])
    Session.add_all((m1, m2, m3))


    w = ReEatWidget()
    w.show()

    app.exec_()
    sys.exit()

