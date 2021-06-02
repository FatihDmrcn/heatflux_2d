import PyQt5.QtWidgets as Qtw
from src import main_gui


if __name__ == "__main__":
    app = Qtw.QApplication([])
    gui = main_gui.MainClassAsGUI()
    gui.show()
    app.exec_()
