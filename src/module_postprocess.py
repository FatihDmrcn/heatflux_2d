import PyQt5.QtWidgets as Qtw
import PyQt5.QtCore as Qtc
import PyQt5.QtGui as Qtg
import os


class QPostprocess(Qtw.QWidget):

    save_npy = Qtc.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setSizePolicy(Qtw.QSizePolicy.MinimumExpanding, Qtw.QSizePolicy.Fixed)
        self.title = Qtw.QLabel("Post-Processing")
        self.title.setFont(Qtg.QFont('Times', 12))
        self.title.setAlignment(Qtc.Qt.AlignmentFlag(0x0044))

        self.dir_path = os.getcwd()

        self.button_set_directory = Qtw.QPushButton("Choose directory")
        self.button_set_directory.clicked.connect(self.set_directory)

        self.button_save_results = Qtw.QPushButton("Save .npy")
        self.button_save_results.clicked.connect(self.save_results)

        self.label_path = Qtw.QLineEdit(self.dir_path)

        grid = Qtw.QGridLayout()
        grid.addWidget(self.title, 0, 0, 1, 2)
        grid.addWidget(self.label_path, 1, 0, 1, 2)
        grid.addWidget(self.button_set_directory, 2, 0, 1, 1)
        grid.addWidget(self.button_save_results, 2, 1, 1, 1)
        self.setLayout(grid)

    def set_directory(self):
        self.dir_path = Qtw.QFileDialog.getExistingDirectory(self, "Choose Directory")
        self.label_path.setText(self.dir_path)

    def save_results(self):
        self.save_npy.emit(self.label_path.text())
