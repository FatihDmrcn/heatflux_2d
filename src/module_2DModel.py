import numpy as np
import PyQt5.QtCore as Qtc
from . import module_diagonal


class Model2D(Qtc.QObject):

    send_model = Qtc.pyqtSignal(object)

    def __init__(self, params):
        super().__init__()
        # Parameters
        self.parameters = {'increments': {'t': np.nan, 'x': np.nan, 'y': np.nan},
                           'dimensions': {'t': np.nan, 'x': np.nan, 'y': np.nan},
                           'properties': {'K': np.nan, 'rho': np.nan, 'c': np.nan},
                           'steps': {'t': np.nan, 'x': np.nan, 'y': np.nan},
                           'blocks': {'F': np.nan, 'N': np.nan, 'S': np.nan, 'W': np.nan, 'E': np.nan}}
        # Arrays
        self.u0, self.bic = np.nan, np.nan
        # Coefficient matrix
        self.A = np.nan
        # Auxiliary
        self.sigma, self.alpha, self.beta, self.gamma = np.nan, np.nan, np.nan, np.nan
        # Set values
        for param_type in self.parameters:
            for p in self.parameters[param_type]:
                self.parameters[param_type][p] = params[param_type][p]
        self.calculate_auxiliaries()
        self.calculate_arrays()

    def get_increments(self): return self.parameters['increments']
    def get_dimensions(self): return self.parameters['dimensions']
    def get_properties(self): return self.parameters['properties']
    def get_steps(self): return self.parameters['steps']
    def get_blocks(self): return self.parameters['blocks']
    def get_parameters(self): return self.parameters
    def get_u0(self): return self.u0
    def get_bic(self): return self.bic

    def calculate_A(self):
        self.A = module_diagonal.coefficient_diagonal_matrix(self.parameters['steps']['x'],
                                                             self.parameters['steps']['y'],
                                                             self.alpha, self.beta, self.gamma,
                                                             self.bic.flatten())

    def calculate_auxiliaries(self):
        self.sigma = self.parameters['properties']['K']/(self.parameters['properties']['c']*self.parameters['properties']['rho'])
        self.alpha = self.sigma*self.parameters['increments']['t']/self.parameters['increments']['x']**2
        self.beta = self.sigma*self.parameters['increments']['t']/self.parameters['increments']['y']**2
        self.gamma = - 2*self.alpha - 2*self.beta

    def calculate_arrays(self):
        self.bic = np.zeros((self.parameters['steps']['y'], self.parameters['steps']['x']), dtype=str)
        self.bic[:, :] = 'F'
        self.bic[:1, :] = 'N'
        self.bic[-1:, :] = 'S'
        self.bic[:, :1] = 'W'
        self.bic[:, -1:] = 'E'
        self.u0 = np.zeros_like(self.bic, dtype=float)
        self.u0[:] = [[self.parameters['blocks'][j] for j in i] for i in self.bic]

    @Qtc.pyqtSlot(dict, np.ndarray, np.ndarray)
    def update(self, params, u0, bic):
        # Set arrays
        self.u0 = u0
        self.bic = bic
        # Set Parameters
        for param_type in self.parameters:
            for p in self.parameters[param_type]:
                self.parameters[param_type][p] = params[param_type][p]
        self.calculate_auxiliaries()

    @Qtc.pyqtSlot()
    def model_reference(self):
        self.calculate_A()
        self.send_model.emit(self)

    def F(self, u_flattened):
        return np.dot(self.A, u_flattened)
