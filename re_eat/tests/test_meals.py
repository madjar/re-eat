from re_eat.tests.common import TestCase, get_app
from PyQt4.QtCore import Qt, QIODevice, QDataStream, QByteArray, QMimeData

class MealWidgetTestCase(TestCase):
    def setUp(self):
        super(MealWidgetTestCase, self).setUp()
        self.app = get_app()

    def _get_one(self):
        import datetime
        from re_eat.meals import MealWidget
        return MealWidget(datetime.date(2012,12,12))

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
                             [(1, mw.date),
                              (2, mw.date)])

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
