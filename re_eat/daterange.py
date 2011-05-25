import datetime
from PyQt4.QtGui import QDateEdit, QDialog, QVBoxLayout, QLabel, QDialogButtonBox

class DateRangeDialog(QDialog):
    def __init__(self):
        super(DateRangeDialog, self).__init__()
        self._fro = QDateEdit(datetime.date.today())
        self._to = QDateEdit(datetime.date.today()
                            + datetime.timedelta(4))

        self._fro.dateChanged.connect(self._check_valid_range)
        self._to.dateChanged.connect(self._check_valid_range)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok)
        self.buttons.accepted.connect(self.accept)

        layout = QVBoxLayout()
        layout.addWidget(QLabel('Please select a date range'))
        layout.addWidget(self._fro)
        layout.addWidget(self._to)
        layout.addWidget(self.buttons)
        self.setLayout(layout)


    def _check_valid_range(self):
        self.buttons.button(QDialogButtonBox.Ok)\
            .setEnabled(self._fro.date() <= self._to.date())

    @property
    def fro(self):
        return self._fro.date().toPyDate()

    @property
    def to(self):
        return self._to.date().toPyDate()