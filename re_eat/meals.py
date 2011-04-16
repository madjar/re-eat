import datetime
from PyQt4.QtCore import Qt, QDataStream, QIODevice, pyqtSignal
from PyQt4.QtGui import QListWidget, QListWidgetItem

class MealWidget(QListWidget):
    recipeAdded = pyqtSignal([int, datetime.date])

    def __init__(self, date, parent=None):
        super(MealWidget, self).__init__(parent)
        self.date = date
        self.viewport().setAcceptDrops(True)
        self.setDropIndicatorShown(True)

    def addRecipe(self, recipe):
        item = QListWidgetItem(recipe.name, self)
        item.setData(Qt.UserRole, recipe.id)

    def refreshWithRecipes(self, recipes):
        self.clear()
        for r in recipes:
            self.addRecipe(r)

    def removeRecipe(self, recipe):
        for i in range(self.count()):
            id, _ = self.item(i).data(Qt.UserRole).toInt()
            if id == recipe.id:
                self.takeItem(i)
                return

    def mimeTypes(self):
        return ['application/vnd.re-eat.recipe']

    def supportedDropActions(self):
        return Qt.CopyAction | Qt.MoveAction

    def dropMimeData(self, index, data, action):
        if action == Qt.IgnoreAction:
            return True

        if data.hasFormat('application/vnd.re-eat.recipe'):
            encodedData = data.data('application/vnd.re-eat.recipe')
            stream = QDataStream (encodedData, QIODevice.ReadOnly)

            while not stream.atEnd():
                id = stream.readInt()
                self.recipeAdded.emit(id, self.date)
            return True
        return False
