import PyQt5.QtWidgets as Qtw
import PyQt5.QtCore as Qtc
import module_2DModel
import module_preprocess
import module_process
import module_postprocess
import module_tab
import module_misc


params = {'increments': {'t': 0.01, 'x': 1., 'y': 1.},
          'dimensions': {'t': 20, 'x': 100, 'y': 70},
          'properties': {'K': 16., 'rho': 1., 'c': 1.},
          'steps': {'t': 2000, 'x': 100, 'y': 70},
          'blocks': {'F': 300., 'N': 700., 'S': 700., 'W': 700., 'E': 700.}}


class MainClassAsGUI(Qtw.QWidget):

    apply_model = Qtc.pyqtSignal()
    request_model = Qtc.pyqtSignal()
    delete_old_computed_arrays = Qtc.pyqtSignal()
    STANDARD_MESSAGE = 'You can now set up your model and calculate'

    def __init__(self):
        super().__init__()
        self.setWindowTitle('2D-Heat')

        self.model = module_2DModel.Model2D(params)
        self.setting_up = True

        # MENU
        self.preprocess = module_preprocess.QPreprocess(self.model.get_parameters(), self.model.get_u0(), self.model.get_bic())
        self.preprocess.setEnabled(self.setting_up)
        self.button = Qtw.QPushButton('APPLY MODEL PARAMETERS')
        self.process = module_process.QProcess()
        self.process.setEnabled(not self.setting_up)
        self.postprocess = module_postprocess.QPostprocess()
        self.postprocess.setEnabled(False)

        self.label = Qtw.QLabel(self.STANDARD_MESSAGE)

        self.tab = module_tab.QTabWindow(self.model.get_steps()['x'], self.model.get_steps()['y'], self.model.get_u0())

        ###
        # ALL extra SIGNALS and SLOTS for the main gui
        # Update array Tab with this signal-slot
        self.preprocess.array_data.connect(self.tab.update)
        # Define actions of button click
        self.button.clicked.connect(self.button_event)
        # Delete previously computed arrays from tab widget
        self.delete_old_computed_arrays.connect(self.tab.delete_arrays)
        # Trigger preprocess module to emit params
        self.apply_model.connect(self.preprocess.button_event)
        # Update model with chosen parameters
        self.preprocess.model.connect(self.model.update)
        # Update model with chosen solver_name
        self.preprocess.solver.connect(self.process.set_solver)
        # Trigger model by process module to send the model
        self.request_model.connect(self.model.model_reference)
        self.model.send_model.connect(self.process.set_model)
        # Emit signal that calculation has started/stopped
        self.process.startedCalculation.connect(self.calculation_started)
        self.process.startedCalculation.connect(self.tab.delete_arrays)
        self.process.endedCalculation.connect(self.calculation_ended)
        # Update label by messages from process module
        self.process.signal_message.connect(self.set_standard_text)
        # Save computed arrays by process module
        self.process.array_data.connect(self.tab.save_array)
        # Enable visualization of results
        self.process.show_results.connect(self.tab.show_results)
        # Save results as .npy
        self.postprocess.save_npy.connect(self.tab.save_results)
        ###

        self.vbox_menu = Qtw.QVBoxLayout()
        self.vbox_menu.setAlignment(Qtc.Qt.AlignTop)
        self.vbox_menu.addWidget(self.preprocess)
        self.vbox_menu.addWidget(self.button)
        self.vbox_menu.addWidget(self.process)
        self.vbox_menu.addWidget(self.postprocess)
        self.vbox_menu.addWidget(module_misc.QSpacer(Qtw.QSizePolicy.Fixed, Qtw.QSizePolicy.Expanding))
        self.vbox_menu.addWidget(self.label)
        self.menu = Qtw.QFrame()
        self.menu.setSizePolicy(Qtw.QSizePolicy.Fixed, Qtw.QSizePolicy.Expanding)
        self.menu.setLayout(self.vbox_menu)

        layout = Qtw.QHBoxLayout()
        layout.addWidget(self.menu)
        layout.addWidget(self.tab)
        self.setLayout(layout)

        self.show()

    @Qtc.pyqtSlot(bool)
    def set_process_state(self, preprocess_state): self.process.setEnabled(not preprocess_state)

    def button_event(self):
        # If current state is 'setting up', emit signal, so that preprocessing module is triggered to emit model params
        self.delete_old_computed_arrays.emit()
        if self.setting_up:
            self.apply_model.emit()
            self.request_model.emit()
            self.button.setText('GO BACK TO SETTING UP THE MODEL')
        if not self.setting_up:
            self.button.setText('APPLY MODEL PARAMETERS')
        # Inverse setting up state and Enable/Disable widgets
        self.setting_up = not self.setting_up
        self.preprocess.setEnabled(self.setting_up)
        self.process.setEnabled(not self.setting_up)
        self.postprocess.setEnabled(False)

    @Qtc.pyqtSlot(str)
    def set_standard_text(self, message):
        self.STANDARD_MESSAGE = message
        self.label.setText(self.STANDARD_MESSAGE)

    def calculation_started(self):
        self.button.setEnabled(False)

    def calculation_ended(self):
        self.button.setEnabled(True)
        self.postprocess.setEnabled(True)
