from PyQt4.QtCore import QAbstractListModel, Qt, QMimeData, QDataStream, QByteArray, QIODevice
from PyQt4.QtGui import QListWidget, QListWidgetItem
from re_eat.models import Session, Recipe, Tag

def get_recipes(tags=()):
    recipes = Session.query(Recipe)
    for t in tags:
        recipes = recipes.filter(Recipe.tags.any(Tag.id == t))
    return recipes.all()

class RecipesWidget(QListWidget):
    def __init__(self, parent=None):
        super(RecipesWidget, self).__init__(parent)
        self.setDragEnabled(True)
        self.setSelectionMode(self.ExtendedSelection)
        self.model().setSupportedDragActions(Qt.CopyAction)

        self.reload()

    def reload(self, tags=()):
        self.clear()
        for r in get_recipes(tags):
            item = QListWidgetItem(r.name, self)
            item.setData(Qt.UserRole, r.id)

    def mimeTypes(self):
        return ['application/vnd.re-eat.recipe']

    def mimeData(self, items):
        mimeData = QMimeData()
        encodedData = QByteArray()
        stream = QDataStream(encodedData, QIODevice.WriteOnly)
        for item in items:
            id, _ = item.data(Qt.UserRole).toInt()
            stream.writeInt(id)
        mimeData.setData('application/vnd.re-eat.recipe', encodedData)
        return mimeData

