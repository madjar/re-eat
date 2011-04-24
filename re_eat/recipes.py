import datetime
from PyQt4.QtCore import Qt, QMimeData, QDataStream, QByteArray, QIODevice, pyqtSignal
from PyQt4.QtGui import QListWidget, QListWidgetItem
from re_eat.models import Session, Recipe, Tag


def get_recipes(tags=()):
    recipes = Session.query(Recipe)
    for t in tags:
        recipes = recipes.filter(Recipe.tags.any(Tag.id == t))
    return recipes.all()


class RecipesWidget(QListWidget):
    recipeRemoved = pyqtSignal([int, datetime.date, int])

    def __init__(self, parent=None):
        super(RecipesWidget, self).__init__(parent)
        self.setDragEnabled(True)
        self.setSelectionMode(self.ExtendedSelection)
        self.model().setSupportedDragActions(Qt.CopyAction)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(False)

        self.reload()

    def reload(self, tags=()):
        self.clear()
        for r in get_recipes(tags):
            item = QListWidgetItem(r.name, self)
            item.setData(Qt.UserRole, r.id)

    def mimeTypes(self):
        return ['application/vnd.re-eat.recipe',
                'application/vnd.re-eat.meal_recipe']

    def mimeData(self, items):
        mimeData = QMimeData()
        encodedData = QByteArray()
        stream = QDataStream(encodedData, QIODevice.WriteOnly)
        for item in items:
            id = item.data(Qt.UserRole)
            stream.writeInt(id)
        mimeData.setData('application/vnd.re-eat.recipe', encodedData)
        return mimeData

    def dropMimeData(self, index, data, action):
        if action == Qt.IgnoreAction:
            return True

        if data.hasFormat('application/vnd.re-eat.meal_recipe'):
            encodedData = data.data('application/vnd.re-eat.meal_recipe')
            stream = QDataStream(encodedData, QIODevice.ReadOnly)

            while not stream.atEnd():
                id = stream.readInt()
                date = stream.readQVariant()
                index = stream.readInt()
                self.recipeRemoved.emit(id, date, index)
            return True
        return False
