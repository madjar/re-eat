# -*- coding: utf-8 -*-

import sip
sip.setapi('QString', 2)
sip.setapi('QDate', 2)
sip.setapi('QVariant', 2)

import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from re_eat.models import initialize_sql
from re_eat.meals import PlanningWidget
from re_eat.tags import TagsWidget
from re_eat.recipes import RecipesWidget
from re_eat.daterange import DateRangeDialog
from re_eat.config import database_url


class ReEatWidget(QSplitter):
    def __init__(self, fro, to):
        super(ReEatWidget, self).__init__(Qt.Horizontal)

        left = QSplitter(Qt.Vertical)
        rw = RecipesWidget()
        tw = TagsWidget()
        tw.tagsChanged.connect(rw.reload)
        rw.recipeChanged.connect(tw.reload)
        left.addWidget(rw)
        left.addWidget(tw)

        self.addWidget(left)

        right = PlanningWidget(fro, to)
        rw.recipeRemoved.connect(right._recipe_removed)
        self.addWidget(right)


def main():
    app = QApplication(sys.argv)

    initialize_sql(database_url())

    drd = DateRangeDialog()
    if not drd.exec_():
        sys.exit(-1)

    w = ReEatWidget(drd.fro, drd.to)
    w.show()

    sys.exit(app.exec_())
