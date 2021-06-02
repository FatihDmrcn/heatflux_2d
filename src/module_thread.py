import PyQt5.QtCore as Qtc
import time


class QThreadSleep(Qtc.QThread):
    threadFinished = Qtc.pyqtSignal()

    def __init__(self):
        super().__init__()

    def run(self):
        time.sleep(5)
        self.threadFinished.emit()


class QThreadIntegrate(Qtc.QThread):
    threadFinished = Qtc.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.solver = None

    def set_solver(self, solver):
        self.solver = solver

    def run(self):
        self.solver.integrate()
        self.threadFinished.emit()
