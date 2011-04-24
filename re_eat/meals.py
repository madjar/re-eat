import datetime
from PyQt4.QtCore import Qt, QDataStream, QIODevice, pyqtSignal, QMimeData, QByteArray, QVariant
from PyQt4.QtGui import QListWidget, QListWidgetItem, QWidget,\
    QScrollArea, QFormLayout, QHBoxLayout
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.expression import and_
from re_eat.models import Session, Meal, Recipe

MAX_INDEX = 2


def daterange(start_date, end_date):
    for n in range((end_date - start_date).days):
        yield start_date + datetime.timedelta(n)


class MealWidget(QListWidget):
    recipeAdded = pyqtSignal([int, datetime.date, int])
    recipeMoved = pyqtSignal([int, datetime.date, int, datetime.date, int])

    def __init__(self, date, index, parent=None):
        super(MealWidget, self).__init__(parent)
        self.date = date
        self.index = index
        self.setAcceptDrops(True)
        self.setDragEnabled(True)

    def addRecipe(self, recipe):
        item = QListWidgetItem(recipe.name, self)
        item.setData(Qt.UserRole, recipe.id)

    def refreshWithRecipes(self, recipes):
        self.clear()
        for r in recipes:
            self.addRecipe(r)

    def removeRecipe(self, recipe):
        for i in range(self.count()):
            id = self.item(i).data(Qt.UserRole)
            if id == recipe.id:
                self.takeItem(i)
                return

    def mimeTypes(self):
        return ['application/vnd.re-eat.meal_recipe',
                'application/vnd.re-eat.recipe']

    def supportedDropActions(self):
        return Qt.CopyAction

    def dropMimeData(self, index, data, action):
        if action == Qt.IgnoreAction:
            return True

        if data.hasFormat('application/vnd.re-eat.recipe'):
            encodedData = data.data('application/vnd.re-eat.recipe')
            stream = QDataStream(encodedData, QIODevice.ReadOnly)

            while not stream.atEnd():
                id = stream.readInt()
                self.recipeAdded.emit(id, self.date, self.index)
            return True
        elif data.hasFormat('application/vnd.re-eat.meal_recipe'):
            encodedData = data.data('application/vnd.re-eat.meal_recipe')
            stream = QDataStream(encodedData, QIODevice.ReadOnly)

            while not stream.atEnd():
                id = stream.readInt()
                date = stream.readQVariant()
                index = stream.readInt()
                self.recipeMoved.emit(id, date, index, self.date, self.index)
            return True
        return False

    def mimeData(self, items):
        mimeData = QMimeData()
        encodedData = QByteArray()
        stream = QDataStream(encodedData, QIODevice.WriteOnly)
        for item in items:
            id = item.data(Qt.UserRole)
            stream.writeInt(id)
            stream.writeQVariant(self.date)
            stream.writeInt(self.index)
        mimeData.setData('application/vnd.re-eat.meal_recipe', encodedData)
        return mimeData


class PlanningWidget(QScrollArea):
    def __init__(self, fro, to, parent=None):
        super(PlanningWidget, self).__init__(parent)
        self.fro = fro
        self.to = to

        # Create widget
        widget = QWidget()
        self.boxLayout = QHBoxLayout()
        self.columns = []
        self.widgets = {}
        for index in xrange(MAX_INDEX):
            formLayout = QFormLayout()
            self.columns.append(formLayout)
            self.boxLayout.addLayout(formLayout)
            for date in daterange(fro, to):
                self._add_widget_for_date(date, index)

        widget.setLayout(self.boxLayout)
        self.setWidgetResizable(True)
        self.setWidget(widget)

        # Populate widgets
        for meal in self._meals_in_range():
            self.widgets[(meal.date, meal.index)]\
                .refreshWithRecipes(meal.recipes)

    def _meals_in_range(self):
        return (Session.query(Meal).options(joinedload('recipes'))
                .filter(and_(self.fro <= Meal.date, Meal.date < self.to))
                .all())

    def _add_widget_for_date(self, date, index):
        mw = MealWidget(date, index, self)
        mw.setMinimumHeight(48)
        mw.setMaximumHeight(64)
        mw.recipeAdded.connect(self._recipe_added)
        mw.recipeMoved.connect(self._recipe_moved)
        self.columns[index].addRow(date.strftime('%A %d %B'), mw)
        self.widgets[(date, index)] = mw


    def get_meal(self, date, index):
        try:
            meal = (Session.query(Meal).
                    filter(and_(Meal.date == date, Meal.index == index))
                    .one())
        except NoResultFound:
            meal = Meal(date, index)
            Session.add(meal)
        return meal

    def add_recipe(self, id, date, index):
        meal = self.get_meal(date, index)
        recipe = Session.query(Recipe).get(id)
        meal.recipes.append(recipe)
        self.widgets[(date, index)].addRecipe(recipe)

    def remove_recipe(self, id, date, index):
        meal = self.get_meal(date, index)
        recipe = Session.query(Recipe).get(id)
        meal.recipes.remove(recipe)
        self.widgets[(date, index)].removeRecipe(recipe)

    def _recipe_added(self, id, date, index):
        self.add_recipe(id, date, index)

    def _recipe_moved(self, id, date_from, index_from, date_to, index_to):
        self.remove_recipe(id, date_from, index_from)
        self.add_recipe(id, date_to, index_to)

    def _recipe_removed(self, id, date, index):
        self.remove_recipe(id, date, index)
