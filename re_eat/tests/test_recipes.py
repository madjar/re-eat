# -*- coding: utf-8 -*-
from re_eat.tests.common import TestCase

import sys
from PyQt4.QtGui import QApplication
from re_eat.models import Session, Tag, Recipe
from re_eat.recipes import RecipesWidget, get_recipes


def load_some_tags():
    t1 = Tag(u'pâtes')
    t2 = Tag(u'tomate')
    r1 = Recipe(u'carbonara')
    r1.tags = [t1]
    r2 = Recipe(u'bolognaise')
    r2.tags = [t1, t2]
    r3 = Recipe(u'tomates farcies')
    r3.tags = [t2]
    r4 = Recipe(u'saucisses-purée')

    tags = [t1, t2]
    recipes = [r1, r2, r3, r4]
    Session.add_all(tags)
    Session.add_all(recipes)
    Session.commit()
    return tags, recipes

class GetRecipesFromTagsTestCase(TestCase):
    def setUp(self):
        super(GetRecipesFromTagsTestCase, self).setUp()
        self.tags, self.recipes = load_some_tags()

    def test_all_the_recipes_when_no_tag_selected(self):
        recipes = get_recipes()
        self.assertListEqual(recipes, self.recipes)

    def test_recipes_when_one_tag_is_selected(self):
        recipes = get_recipes([self.tags[0].id])
        self.assertListEqual(recipes, self.recipes[0:2])

    def test_recipes_when_multiple_tags_are_selected(self):
        recipes = get_recipes([t.id for t in self.tags])
        self.assertListEqual(recipes, [self.recipes[1]])


class RecipesWidgetTestCase(TestCase):
    def setUp(self):
        super(RecipesWidgetTestCase, self).setUp()
        self.tags, self.recipes = load_some_tags()

        self.app = QApplication(sys.argv)

    def test_the_widget_is_correcty_populated(self):
        rw = RecipesWidget()

        self.assertEqual(rw.count(), 4)
        self.assertEqual(rw.item(0).text(), self.recipes[0].name)
