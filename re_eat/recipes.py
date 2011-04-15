from PyQt4.QtCore import QAbstractListModel, Qt
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

        self.reload()

    def reload(self, tags=()):
        get_recipes(tags)
        self.clear()
        for r in get_recipes(tags):
            item = QListWidgetItem(r.name, self)
            item.setData(Qt.UserRole, r.id)
