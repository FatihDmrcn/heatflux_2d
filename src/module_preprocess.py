import PyQt5.QtWidgets as Qtw
import PyQt5.QtCore as Qtc
import PyQt5.QtGui as Qtg
import numpy as np


class QPreprocess(Qtw.QWidget):

    array_data = Qtc.pyqtSignal(int, int, np.ndarray)
    model = Qtc.pyqtSignal(dict, np.ndarray, np.ndarray)
    solver = Qtc.pyqtSignal(str)

    def __init__(self, params, u, bic):
        super().__init__()
        self.setSizePolicy(Qtw.QSizePolicy.Fixed, Qtw.QSizePolicy.Fixed)
        self.title_align = Qtc.Qt.AlignmentFlag(0x0084)
        self.text_align = Qtc.Qt.AlignmentFlag(0x0082)
        self.text_width = 40
        self.widget_width = 60
        self.preprocess_state = True

        # DATA FOR SIMULATION
        # Init parameters
        self.increments = params['increments']
        self.dimensions = params['dimensions']
        self.properties = params['properties']
        self.steps = params['steps']
        self.blocks = params['blocks']
        # Init variables
        self.u0 = u
        self.bic = bic
        # Init miscellaneous
        self.cfl = {'x': 1., 'y': 1.}

        # Input and display dictionaries
        self.input_increments = {}
        self.input_dimensions = {}
        self.input_properties = {}
        self.label_steps = {}
        self.input_blocks = {}
        self.label_cfl = {}
        # Display cfl numbers
        for i in self.cfl:
            if i not in self.label_cfl:
                self.label_cfl[i] = Qtw.QLabel()
                self.label_cfl[i].setFixedWidth(self.widget_width)
                self.label_cfl[i].setText(str(self.cfl[i]))
        for i in self.steps:
            # Display steps
            if i not in self.label_steps:
                self.label_steps[i] = Qtw.QLabel(str(self.steps[i]))
            # Input of increments
            if i not in self.input_increments:
                self.input_increments[i] = Qtw.QDoubleSpinBox()
                self.input_increments[i].setRange(0.01, 1.)
                self.input_increments[i].setSingleStep(0.01)
                self.input_increments[i].setFixedWidth(self.widget_width)
                self.input_increments[i].setValue(self.increments[i])
            # Input of dimensions
            if i not in self.input_dimensions:
                self.input_dimensions[i] = Qtw.QSpinBox()
                self.input_dimensions[i].setRange(1, 1000)
                self.input_dimensions[i].setFixedWidth(self.widget_width)
                self.input_dimensions[i].setValue(self.dimensions[i])
            self.input_increments[i].valueChanged.connect(self.calculate_values)
            self.input_dimensions[i].valueChanged.connect(self.calculate_values)
        # Input of physical properties
        for i in self.properties:
            if i not in self.input_properties:
                self.input_properties[i] = Qtw.QLineEdit()
                self.input_properties[i].setFixedWidth(self.widget_width)
                self.input_properties[i].setText(str(self.properties[i]))
                self.input_properties[i].textChanged.connect(self.calculate_values)
        # Input of boundary-initial conditions
        for i in self.blocks:
            if i not in self.input_blocks:
                self.input_blocks[i] = Qtw.QLineEdit()
                self.input_blocks[i].setFixedWidth(self.widget_width)
                self.input_blocks[i].setText(str(self.blocks[i]))
                self.input_blocks[i].textChanged.connect(self.calculate_values)
        # Selecting desired solver_name
        self.combo_solver = Qtw.QComboBox()
        self.combo_solver.addItems(['Explicit', 'Implicit'])

        # Adding widgets to frame
        self.grid_preprocess = Qtw.QGridLayout()
        row = 0
        self.title = Qtw.QLabel("Pre-Processing")
        self.title.setFont(Qtg.QFont('Times', 12))
        self.title.setAlignment(Qtc.Qt.AlignmentFlag(0x0044))
        self.grid_preprocess.addWidget(self.title, row, 0, 1, 6)
        row += 1
        title = Qtw.QLabel('Dimensions')
        title.setAlignment(self.title_align)
        self.grid_preprocess.addWidget(title, row, 0, 1, 6)
        row += 1
        for j, i in enumerate(self.dimensions, 0):
            text = Qtw.QLabel(i+":")
            text.setFixedWidth(self.text_width )
            text.setAlignment(self.text_align)
            self.grid_preprocess.addWidget(text, row, 2*j)
            self.grid_preprocess.addWidget(self.input_dimensions[i], row, 2 * j + 1)
        row += 1
        for j, i in enumerate(self.increments, 0):
            text = Qtw.QLabel("d"+i+":")
            text.setFixedWidth(self.text_width)
            text.setAlignment(self.text_align)
            self.grid_preprocess.addWidget(text, row, 2*j)
            self.grid_preprocess.addWidget(self.input_increments[i], row, 2*j+1)
        row += 1
        for j, i in enumerate(self.steps, 0):
            text = Qtw.QLabel("=")
            text.setFixedWidth(self.text_width)
            text.setAlignment(self.text_align)
            self.grid_preprocess.addWidget(text, row, 2*j)
            self.grid_preprocess.addWidget(self.label_steps[i], row, 2*j+1)
        row += 1
        title = Qtw.QLabel('Properties')
        title.setAlignment(self.title_align)
        self.grid_preprocess.addWidget(title, row, 0, 1, 6)
        row += 1
        for j, i in enumerate(self.properties, 0):
            text = Qtw.QLabel(i+":")
            text.setFixedWidth(self.text_width)
            text.setAlignment(self.text_align)
            self.grid_preprocess.addWidget(text, row, 2*j)
            self.grid_preprocess.addWidget(self.input_properties[i], row, 2*j+1)
        row += 1
        title = Qtw.QLabel('Temperatures')
        title.setAlignment(self.title_align)
        self.grid_preprocess.addWidget(title, row, 0, 1, 6)
        row += 1
        for j, i in enumerate(self.blocks, 0):
            text = Qtw.QLabel(i+":")
            text.setFixedWidth(self.text_width)
            text.setAlignment(self.text_align)
            self.grid_preprocess.addWidget(text, row+int(j/3), 2*(j%3))
            self.grid_preprocess.addWidget(self.input_blocks[i], row + int(j / 3), 2 * (j % 3) + 1)
        row += 2
        title = Qtw.QLabel('Solver')
        title.setAlignment(self.title_align)
        self.grid_preprocess.addWidget(title, row, 0, 1, 6)
        row += 1
        self.grid_preprocess.addWidget(self.combo_solver, row, 0, 1, 6)
        row += 1
        for j, i in enumerate(self.cfl, 0):
            text = Qtw.QLabel('CFL_'+i+":")
            text.setFixedWidth(self.text_width )
            text.setAlignment(self.text_align)
            self.grid_preprocess.addWidget(text, row, 2*j)
            self.grid_preprocess.addWidget(self.label_cfl[i], row, 2*j+1)
        self.setLayout(self.grid_preprocess)

        self.calculate_values()

    def set_boundary_initial_array(self):
        # REWRITE
        self.bic = np.zeros((self.steps['y'], self.steps['x']), dtype=str)
        self.bic[:, :] = 'F'
        self.bic[:1, :] = 'N'
        self.bic[-1:, :] = 'S'
        self.bic[:, :1] = 'W'
        self.bic[:, -1:] = 'E'
        self.u0 = np.zeros_like(self.bic, dtype=float)
        self.u0[:] = [[self.blocks[j] for j in i] for i in self.bic]

    # Signal will be emitted by this method
    # @Qtc.pyqtSlot()
    def calculate_values(self):
        # Get steps
        for s in self.steps:
            self.dimensions[s] = self.input_dimensions[s].value()
            self.increments[s] = self.input_increments[s].value()
            self.steps[s] = round(self.dimensions[s]/self.increments[s])
            self.label_steps[s].setText(str(self.steps[s]))
        # Get properties
        for p in self.properties:
            self.properties[p] = float(self.input_properties[p].text())
        sigma = self.properties['K']/(self.properties['c']*self.properties['rho'])
        # Get CFL
        for c in self.cfl:
            self.cfl[c] = (self.increments['t']*2*sigma)/self.increments[c]**2
            self.label_cfl[c].setText(str(self.cfl[c]))
        # Get Temperatures
        for i in self.blocks:
            self.blocks[i] = float(self.input_blocks[i].text())
        self.set_boundary_initial_array()
        self.array_data.emit(self.steps['x'], self.steps['y'], self.u0)

    # Slot, so that button click in MainGUI can trigger this method
    # and the desired Signals will be emitted
    @Qtc.pyqtSlot()
    def button_event(self):
        parameters = {'increments': self.increments,
                      'dimensions': self.dimensions,
                      'properties': self.properties,
                      'steps': self.steps,
                      'blocks': self.blocks}
        self.model.emit(parameters, self.u0, self.bic)
        self.solver.emit(self.combo_solver.currentText())

    def enable_widgets(self):
        self.frame.setEnabled(True)
