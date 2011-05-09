import datetime
import unittest
import mock
from re_eat.tests.common import TestCase, get_app
from re_eat.meals import PlanningWidget, daterange
from re_eat.models import Recipe, Meal, Session
from PyQt4.QtCore import Qt, QIODevice, QDataStream, QByteArray, QMimeData

class DateRangeTestCase(unittest.TestCase):
    def test_date_range(self):
        fro = datetime.date(2012, 12, 12)
        to = datetime.date(2012, 12, 15)
        self.assertListEqual(list(daterange(fro, to)),
                             [datetime.date(2012, 12, 12),
                              datetime.date(2012, 12, 13),
                              datetime.date(2012, 12, 14)])

class MealWidgetTestCase(TestCase):
    def setUp(self):
        super(MealWidgetTestCase, self).setUp()
        self.app = get_app()

    def _get_one(self):
        import datetime
        from re_eat.meals import MealWidget
        return MealWidget(datetime.date(2012, 12, 12), 0)

    def test_the_widget_is_empty(self):
        mw = self._get_one()
        self.assertEqual(mw.count(), 0)

    def test_adding_recipes(self):
        mw = self._get_one()

        recipe = DummyRecipe(1, u"carbo")
        mw.addRecipe(recipe)

        self.assertEqual(mw.count(), 1)
        self.assertEqual(mw.item(0).text(), recipe.name)

    def test_mass_adding_recipes(self):
        mw = self._get_one()
        mw.addRecipe(DummyRecipe(1, u"carbo"))

        mw.refreshWithRecipes([DummyRecipe(1, u""),
                               DummyRecipe(2, u"")])
        self.assertEqual(mw.count(), 2)

    def test_deleting_recipes(self):
        mw = self._get_one()
        recipe = DummyRecipe(1, u"carbo")
        mw.addRecipe(recipe)

        mw.removeRecipe(recipe)

        self.assertEqual(mw.count(), 0)

    def test_dropping_the_data_emits_the_signal(self):
        mw = self._get_one()
        self.assertEqual(mw.supportedDropActions(),
                         Qt.CopyAction)
        self.assertIn('application/vnd.re-eat.recipe', mw.mimeTypes())
        assert mw.viewport().acceptDrops()

        mw.recipeAdded = DummySignal()

        mimeData = QMimeData()
        encodedData = QByteArray()
        stream = QDataStream(encodedData, QIODevice.WriteOnly)
        stream.writeInt(1)
        stream.writeInt(2)
        mimeData.setData('application/vnd.re-eat.recipe', encodedData)

        mw.dropMimeData(0, mimeData, Qt.CopyAction)
        self.assertListEqual(mw.recipeAdded.received,
                             [(1, mw.date, mw.index),
                              (2, mw.date, mw.index)])

        mw.recipeMoved = DummySignal()
        mimeData = QMimeData()
        encodedData = QByteArray()
        stream = QDataStream(encodedData, QIODevice.WriteOnly)
        stream.writeInt(42)
        stream.writeQVariant(datetime.date.today())
        stream.writeInt(2)
        mimeData.setData('application/vnd.re-eat.meal_recipe', encodedData)

        mw.dropMimeData(0, mimeData, Qt.CopyAction)
        self.assertListEqual(mw.recipeMoved.received,
                             [(42, datetime.date.today(), 2, mw.date, mw.index)])

    def test_stupid_drop_case(self):
        mw = self._get_one()
        mw.recipeAdded = DummySignal()
        self.assertEqual(mw.dropMimeData(None, None, Qt.IgnoreAction),
                         True)

        mimeData = QMimeData()
        self.assertEqual(mw.dropMimeData(0, mimeData, Qt.CopyAction),
                         False)
        self.assertEqual(mw.recipeAdded.received, [])

    def test_mime_data(self):
        class DummyItem(object):
            def data(s, role):
                self.assertEqual(role, Qt.UserRole)
                return 42

        mw = self._get_one()
        data = mw.mimeData([DummyItem()]).data('application/vnd.re-eat.meal_recipe')
        stream = QDataStream(data, QIODevice.ReadOnly)
        self.assertEqual(stream.readInt(), 42)
        self.assertEqual(stream.readQVariant(), mw.date)
        self.assertEqual(stream.readInt(), mw.index)


class PlanningWidgetTestCase(TestCase):
    def setUp(self):
        super(PlanningWidgetTestCase, self).setUp()
        self.app = get_app()

    def _get_one(self):
        self.recipe = Recipe('carbo')
        self.m1 = Meal(datetime.date(2010, 01, 01), 0, [self.recipe])
        self.m2 = Meal(datetime.date(2010, 01, 05), 1, [self.recipe])
        Session.add_all([self.recipe, self.m1, self.m2])

        fro = datetime.date(2010, 01, 01)
        to = datetime.date(2010, 01, 10)
        pw = PlanningWidget(fro, to)
        return pw

    def test_we_got_the_right_meals(self):
        recipe = Recipe('carbo')
        m1 = Meal(datetime.date(2010, 01, 01), 0, [recipe])
        m2 = Meal(datetime.date(2010, 01, 05), 0, [recipe])
        m3 = Meal(datetime.date(2010, 01, 12), 1, [recipe])
        Session.add_all((recipe, m1, m2, m3))

        obj = mock.Mock(PlanningWidget)
        obj.fro = datetime.date(2010, 01, 01)
        obj.to = datetime.date(2010, 01, 10)

        self.assertEqual(PlanningWidget._meals_in_range(obj),
                         [m1, m2])

    def test_the_widget_is_correctly_initialized(self):
        pw = self._get_one()

        self.assertEqual(pw.widgets[(self.m1.date, self.m1.index)].item(0).text(),
                         'carbo')

    def test_get_existing_meal(self):
        pw = self._get_one()
        self.assertEqual(pw.get_meal(self.m1.date, self.m1.index),
                         self.m1)

    def test_get_new_meal(self):
        pw = self._get_one()
        date = datetime.date(2010, 01, 03)
        index = 2
        meal = pw.get_meal(date, index)
        self.assertEqual(meal.date, date)
        self.assertEqual(meal.index, index)

    def test_recipe_added(self):
        pw = self._get_one()
        date = datetime.date(2010, 01, 03)
        index = 1
        pw._recipe_added(self.recipe.id, date, index)
        self.assertEqual(pw.get_meal(date, index).recipes,
                         [self.recipe])
        self.assertEqual(pw.widgets[(date, index)].count(), 1)

    def test_recipe_moved(self):
        pw = self._get_one()
        arg1 = (datetime.date(2010, 01, 01), 0)
        arg2 = (datetime.date(2010, 01, 03), 1)
        pw._recipe_moved(self.recipe.id, arg1[0], arg1[1], *arg2)
        self.assertEqual(pw.get_meal(*arg1).recipes,
                         [])
        self.assertEqual(pw.widgets[arg1].count(), 0)
        self.assertEqual(pw.get_meal(*arg2).recipes,
                         [self.recipe])
        self.assertEqual(pw.widgets[arg2].count(), 1)

    def test_recipe_removed(self):
        pw = self._get_one()
        arg = (datetime.date(2010, 01, 01), 0)
        pw._recipe_removed(self.recipe.id, *arg)
        self.assertEqual(pw.get_meal(*arg).recipes,
                         [])
        self.assertEqual(pw.widgets[arg].count(), 0)



class DummyRecipe(object):
    def __init__(self, id, name, description=''):
        self.id = id
        self.name = name
        self.description = description


class DummySignal(object):
    def __init__(self):
        self.received = []

    def emit(self, *args):
        self.received.append(args)
