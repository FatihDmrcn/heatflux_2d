import PyQt5.QtWidgets as Qtw
import PyQt5.QtCore as Qtc
import PyQt5.QtGui as Qtg
import numpy as np
from . import module_thread
from . import module_2DSolver


class QProcess(Qtw.QWidget):

    signal_message = Qtc.pyqtSignal(str)
    array_data = Qtc.pyqtSignal(int, int, np.ndarray)
    save_data = Qtc.pyqtSignal(np.ndarray)
    stopCalculation = Qtc.pyqtSignal()
    startedCalculation = Qtc.pyqtSignal()
    endedCalculation = Qtc.pyqtSignal()
    show_results = Qtc.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setSizePolicy(Qtw.QSizePolicy.MinimumExpanding, Qtw.QSizePolicy.Fixed)
        self.solver_name = 'None'
        self.solver = None
        self.model = None
        self.success = True
        # Widgets
        self.title = Qtw.QLabel("Processing")
        self.title.setFont(Qtg.QFont('Times', 12))
        self.title.setAlignment(Qtc.Qt.AlignmentFlag(0x0044))
        self.button_calculate = Qtw.QPushButton('Calculate')
        self.button_calculate.clicked.connect(self.calculate)
        self.progressBar = Qtw.QProgressBar(self)
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(100)
        self.progressBar.setTextVisible(False)
        self.progressBar.setValue(0)
        self.button_abort = Qtw.QPushButton('Abort')
        self.button_abort.clicked.connect(self.abort_calculation)
        # Adding widgets to layout
        self.grid_process = Qtw.QVBoxLayout()
        self.grid_process.setAlignment(Qtc.Qt.AlignTop)
        self.grid_process.addWidget(self.title)
        self.grid_process.addWidget(self.button_calculate)
        self.grid_process.addWidget(self.progressBar)
        self.grid_process.addWidget(self.button_abort)
        self.setLayout(self.grid_process)

        self.thread_integrate = module_thread.QThreadIntegrate()
        self.thread_integrate.threadFinished.connect(self.finished_calculation)

        self.thread_sleep = module_thread.QThreadSleep()
        self.thread_sleep.threadFinished.connect(self.set_standard_text)

    @Qtc.pyqtSlot(str)
    def set_solver(self, solver):
        self.solver_name = solver

    @Qtc.pyqtSlot(object)
    def set_model(self, reference):
        self.model = reference

    @Qtc.pyqtSlot(bool)
    def set_success(self, success):
        self.success = success

    def abort_calculation(self):
        self.stopCalculation.emit()

    def finished_calculation(self):
        self.apply_sleep()
        self.show_results.emit()

    def apply_sleep(self):
        if self.success:
            self.signal_message.emit('Finished Calculation')
        if not self.success:
            self.signal_message.emit('Aborted Calculation')
        self.endedCalculation.emit()
        self.button_calculate.setEnabled(True)
        self.thread_sleep.start()
        self.progressBar.setValue(0)

    @Qtc.pyqtSlot()
    def set_standard_text(self):
        self.signal_message.emit('You can now set up your model and calculate')

    def update_progress(self, current, final):
        progress = current/final
        self.signal_message.emit('Progress: {:.0%}'.format(progress))
        self.progressBar.setValue(int(progress*100))

    def calculate(self):
        self.button_calculate.setEnabled(False)
        self.startedCalculation.emit()
        if self.solver_name == 'Explicit':
            self.solver = module_2DSolver.Explicit(self.model)

        if self.solver_name == 'Implicit':
            self.solver = module_2DSolver.Implicit(self.model)

        # Solver related connections of signals and slots
        self.solver.current_status.connect(self.update_progress)
        self.solver.success_status.connect(self.set_success)
        self.stopCalculation.connect(self.solver.abort_calculation)
        self.solver.array_data.connect(self.save_array)

        self.thread_integrate.set_solver(self.solver)
        self.thread_integrate.start()

    @Qtc.pyqtSlot(int, int, np.ndarray)
    def save_array(self, x, y, u):
        self.array_data.emit(x, y, u)
