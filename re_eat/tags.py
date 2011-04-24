from PyQt4.QtCore import QTimer, pyqtSignal, Qt
from PyQt4.QtGui import QCompleter, QStringListModel,\
    QLineEdit, QWidget, QListWidget, QVBoxLayout
from re_eat.models import Session, Tag


class TagLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super(TagLineEdit, self).__init__(parent)
        self.setCompleter(QCompleter())
        self.completer().setModel(QStringListModel())

        self.textChanged.connect(self.whenTextChanged)

    def focusInEvent(self, event):
        QLineEdit.focusInEvent(self, event)
        if self.completer() and not self.completer().popup().isVisible():
            self.completer().complete()

    def whenTextChanged(self):
        if not self.text():
            self.completer().setCompletionPrefix(u"")
            self.completer().complete()


class TagsWidget(QWidget):
    tagsChanged = pyqtSignal(list)

    def __init__(self, parent=None):
        super(TagsWidget, self).__init__(parent)
        self.lineEdit = TagLineEdit(self)
        self.lineEdit.returnPressed.connect(
            lambda: QTimer.singleShot(0, self.addTag))
        self.listWidget = QListWidget(self)
        l = QVBoxLayout(self)
        l.addWidget(self.lineEdit)
        l.addWidget(self.listWidget)

        self.availableTags = []
        self.reload()

    def reload(self):
        tags = Session.query(Tag.name, Tag.id).all()
        self.tagsdict = dict(tags)
        self.availableTags = self.tagsdict.keys()
        for i in xrange(self.listWidget.count()):
            tag = self.listWidget.item(i).text()
            if tag in self.availableTags:
                self.availableTags.remove(tag)
        self.lineEdit.completer().model().setStringList(self.availableTags)

    def addTag(self):
        text = self.lineEdit.text()
        if text in self.availableTags:
            self.availableTags.remove(text)
            self.lineEdit.completer().model().setStringList(self.availableTags)
            self.listWidget.addItem(text)
            self.lineEdit.clear()
            self.tagsChanged.emit(self.tags())

    def tags(self):
        tags = [self.tagsdict[self.listWidget.item(i).text()]
                for i in xrange(self.listWidget.count())]
        return tags

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            self.listWidget.takeItem(self.listWidget.currentRow())
            self.tagsChanged.emit(self.tags())
        else:
            super(TagsWidget, self).keyPressEvent(event)
