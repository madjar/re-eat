import datetime
from PyQt4.QtCore import Qt, QMimeData, QDataStream, QByteArray, QIODevice, pyqtSignal
from PyQt4.QtGui import QListWidget, QListWidgetItem, QDialog, QFormLayout, QLineEdit, QPlainTextEdit, QDialogButtonBox, QHBoxLayout
from re_eat.models import Session, Recipe, Tag


def get_recipes(tags=()):
    recipes = Session.query(Recipe)
    for t in tags:
        recipes = recipes.filter(Recipe.tags.any(Tag.id == t))
    return recipes.all()


class RecipesWidget(QListWidget):
    recipeRemoved = pyqtSignal([int, datetime.date, int])
    recipeChanged = pyqtSignal()

    def __init__(self, parent=None):
        super(RecipesWidget, self).__init__(parent)
        self.setDragEnabled(True)
        self.setSelectionMode(self.ExtendedSelection)
        self.model().setSupportedDragActions(Qt.CopyAction)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(False)

        self.itemDoubleClicked.connect(self.doubleClick)

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


    def doubleClick(self, item):
        recipe = Session.query(Recipe).get(item.data(Qt.UserRole))
        self.editRecipe(recipe)

    def editRecipe(self, recipe):
        if RecipeEditionDialog(recipe, self).exec_():
            self.reload()
            self.recipeChanged.emit()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            # Pas de confirmation, pas de sauvegarde : on est des oufs !
            ids = [item.data(Qt.UserRole) for item in self.selectedItems()]
            Session.query(Recipe).filter(Recipe.id.in_(ids)).delete('fetch')
            self.reload()
        elif event.key() == Qt.Key_N:
            self.editRecipe(None)
        else:
            super(RecipesWidget, self).keyPressEvent(event)


class RecipeEditionDialog(QDialog):
    def __init__(self, recipe = None, parent = None):
        super(RecipeEditionDialog, self).__init__(parent)

        self.setWindowTitle('Recipe edition')

        self.name = QLineEdit()
        self.description = QPlainTextEdit()
        self.tags = QLineEdit()
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        l = QFormLayout(self)
        l.addRow('Name', self.name)
        l.addRow('Description', self.description)
        l.addRow('Tags', self.tags)
        l.addWidget(buttons)


        if recipe:
            self.recipe = recipe
            self.name.setText(recipe.name)
            self.description.setPlainText(recipe.description)
            self.tags.setText(';'.join(t.name for t in recipe.tags))
        else:
            self.recipe = Recipe('')

        self.accepted.connect(self.save_recipe)

    def save_recipe(self):
        self.recipe.name = self.name.text()
        self.recipe.description = self.description.toPlainText()
        self.recipe.tags = [Tag.get(t) for t in self.tags.text().split(';')] if self.tags.text() else []
        Session.add(self.recipe)
