# -*- coding: utf-8 -*-
from re_eat.tests.common import TestCase, get_app

from PyQt4.QtCore import QDataStream, Qt, QMimeData, QByteArray, QIODevice
from PyQt4.QtTest import QTest
from re_eat.models import Session, Tag, Recipe
from re_eat.recipes import RecipesWidget, get_recipes, RecipeEditionDialog
import datetime
import mock


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
    Session.flush()
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
        self.app = get_app()

    def test_the_widget_is_correcty_populated(self):
        rw = RecipesWidget()

        self.assertEqual(rw.count(), 4)
        self.assertEqual(rw.item(0).text(), self.recipes[0].name)

    def test_drag_information_are_correct(self):
        rw = RecipesWidget()
        self.assertIn('application/vnd.re-eat.recipe', rw.mimeTypes())

        items = [rw.item(i) for i in (0, 1)]
        ids = [item.data(Qt.UserRole) for item in items]
        data = rw.mimeData(items)
        stream = QDataStream(data.data('application/vnd.re-eat.recipe'))
        result = []
        while not stream.atEnd():
            result.append(stream.readInt())
        self.assertListEqual(result, ids)

    def test_drag_is_enabled(self):
        rw = RecipesWidget()
        assert rw.dragEnabled()
        assert rw.item(0).flags() & Qt.ItemIsDragEnabled


    def test_dropping_the_data_emits_the_signal(self):
        rw = RecipesWidget()
        self.assertEqual(rw.supportedDropActions(),
                         Qt.CopyAction|Qt.MoveAction)
        self.assertIn('application/vnd.re-eat.meal_recipe', rw.mimeTypes())
        assert rw.viewport().acceptDrops()

        rw.recipeRemoved = DummySignal()

        mimeData = QMimeData()
        encodedData = QByteArray()
        stream = QDataStream(encodedData, QIODevice.WriteOnly)
        stream.writeInt(1)
        stream.writeQVariant(datetime.date.today())
        stream.writeInt(2)
        mimeData.setData('application/vnd.re-eat.meal_recipe', encodedData)

        rw.dropMimeData(0, mimeData, Qt.CopyAction)
        self.assertListEqual(rw.recipeRemoved.received,
                             [(1, datetime.date.today(), 2)])

    def test_stupid_drop_case(self):
        rw = RecipesWidget()
        rw.recipeRemoved = DummySignal()
        self.assertEqual(rw.dropMimeData(None, None, Qt.IgnoreAction),
                         True)

        mimeData = QMimeData()
        self.assertEqual(rw.dropMimeData(0, mimeData, Qt.CopyAction),
                         False)
        self.assertEqual(rw.recipeRemoved.received, [])

    @mock.patch('re_eat.recipes.RecipeEditionDialog')
    def test_double_click_open_the_recipe_dialog(self, mock_dialog):
        r = self.recipes[0]
        rw = RecipesWidget()
        rw.doubleClick(rw.item(0))

        mock_dialog.assert_called_once_with(r, rw)
        mock_dialog(r, rw).exec_.assert_called_once_with()

    def test_remove_recipe(self):
        rw = RecipesWidget()
        self.assertEqual(len(rw.selectedItems()), 0)
        before = Session.query(Recipe).count()

        rw.item(0).setSelected(True)
        rw.item(3).setSelected(True)
        QTest.keyClick(rw, Qt.Key_Delete)

        self.assertEqual(Session.query(Recipe).count(), before - 2)
        self.assertEqual(rw.count(), before - 2)

    def test_key_not_borked(self):
        rw = RecipesWidget()
        previous = rw.currentRow()

        QTest.keyClick(rw, Qt.Key_Down)

        self.assertEqual(rw.currentRow(), previous + 1)


class DummySignal(object):
    def __init__(self):
        self.received = []

    def emit(self, *args):
        self.received.append(args)


class RecipeEditionDialogTestCase(TestCase):
    def setUp(self):
        super(RecipeEditionDialogTestCase, self).setUp()
        self.tags, self.recipes = load_some_tags()
        self.app = get_app()

    def test_create_recipe(self):
        fut = RecipeEditionDialog()
        self.assertEqual(fut.name.text(), '')
        self.assertEqual(fut.description.toPlainText(), '')
        self.assertEqual(fut.tags.text(), '')

        fut.name.setText(u'Endive')
        fut.description.setPlainText(u'desc')
        fut.tags.setText(u'légume')
        tag = Tag(u'légume')
        Session.add(tag)

        fut.accept()

        r = fut.recipe
        self.assertEqual(r.name, u'Endive')
        self.assertEqual(r.description, u'desc')
        self.assertEqual(r.tags, [tag])

    def test_edit_recipe(self):
        r = self.recipes[1]
        fut = RecipeEditionDialog(r)
        self.assertEqual(fut.name.text(), r.name)
        self.assertEqual(fut.description.toPlainText(), r.description)
        self.assertIn(fut.tags.text(), [u'pâtes;tomate',
                                        u'tomate;pâtes'])

        fut.name.setText(u'Endive')
        fut.description.setPlainText(u'desc')
        fut.tags.setText(u'légume')
        tag = Tag(u'légume')
        Session.add(tag)

        fut.accept()

        r = fut.recipe
        self.assertEqual(r.name, u'Endive')
        self.assertEqual(r.description, u'desc')
        self.assertEqual(r.tags, [tag])
