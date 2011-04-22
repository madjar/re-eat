import datetime
import mock
from re_eat.tests.common import TestCase, get_app
from re_eat.meals import PlanningWidget
from re_eat.models import Recipe, Meal, Session
from PyQt4.QtCore import Qt, QIODevice, QDataStream, QByteArray, QMimeData


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
                         Qt.CopyAction | Qt.MoveAction)
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


class PlanningWidgetTestCase(TestCase):
    def setUp(self):
        super(PlanningWidgetTestCase, self).setUp()
        self.app = get_app()

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
