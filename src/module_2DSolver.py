import numpy as np
import PyQt5.QtCore as Qtc


class SingularSystemError(RuntimeError):
    def __init__(self, msg):
        super().__init__(msg)


class NewtonRaphson:
    def __init__(self):
        self.G = np.nan
        self.J = self._J

        self.zStart = np.nan
        self.z = np.nan
        self.r = np.nan
        self._dim = np.nan
        self._nSteps = np.nan

        self.epsilon = 1.e-5
        self.maxSteps = 100
        self.dz = 1e-4

    def set_zStart(self, u_start):
        self.zStart = u_start

    def reInit(self):
        self._dim = len(self.zStart)
        self.r = 1.e100*np.ones(self._dim)
        self.z = self.zStart
        self._nSteps = 0

    def _J(self, z):
        I = np.eye(self._dim)
        r = self.G(z, self.zStart)
        m = []
        for I_i in I:
            m.append((self.G(z + self.dz*I_i, self.zStart) - r)/self.dz)
        J = np.transpose(m)
        return J

    def solve(self):
        self.r = self.G(self.z, self.zStart)
        rMax = max(abs(self.r))
        while rMax > self.epsilon:
            J = self._J(self.z)

            if abs(np.linalg.det(J)) < self.epsilon or self._nSteps > 100:
                raise SingularSystemError("No solution found!")

            step = np.linalg.solve(J, self.r)

            self.z = self.z - step
            self.r = self.G(self.z, self.zStart)
            rMax = max(abs(self.r))
            self._nSteps += 1
            # print('Iterations {}\n'.format(self._nSteps))


class Solver2D(Qtc.QObject):

    current_status = Qtc.pyqtSignal(int, int)
    array_data = Qtc.pyqtSignal(int, int, np.ndarray)
    computed_data = Qtc.pyqtSignal(np.ndarray)
    success_status = Qtc.pyqtSignal(bool)

    def __init__(self, model):
        super().__init__()
        self.model = model
        self.F = model.F
        self.u0 = model.u0

        self.t_steps = model.parameters['steps']['t']
        self.x_steps = model.parameters['steps']['x']
        self.y_steps = model.parameters['steps']['y']

        self.abort = False
        self.reInit()

    @Qtc.pyqtSlot()
    def abort_calculation(self):
        self.abort = True

    def reInit(self):
        self.u = np.repeat(self.u0[:, :, np.newaxis], self.t_steps, axis=2)
        self.I = np.eye(self.x_steps*self.y_steps)

    def integrate(self):
        raise NotImplementedError("Method 'INTEGRATE' not implemented!")


class Explicit(Solver2D):
    def __init__(self, model):
        super().__init__(model)

    def integrate(self):
        t = 0
        for n in range(self.t_steps-1):
            if n % 5 == 0:
                self.array_data.emit(self.x_steps, self.y_steps, self.u[:, :, n])

            u_n = self.u[:, :, n].flatten()
            u_n1 = np.dot(self.I, u_n) + self.F(u_n)
            self.u[:, :, n+1] = np.reshape(u_n1, (self.y_steps, self.x_steps))

            self.current_status.emit(n+1, self.t_steps)
            if self.abort:
                t = n
                break
            t = n
        if t == self.t_steps-2:
            self.success_status.emit(True)
        if t != self.t_steps-2:
            self.success_status.emit(False)
        self.array_data.emit(self.x_steps, self.y_steps, self.u[:, :, t])


class Implicit(Solver2D):
    def __init__(self, model):
        super().__init__(model)
        self.ae_solver = NewtonRaphson()
        self.ae_solver.G = self.G

    def G(self, u_n1, u_n):
        r = u_n + self.F(u_n1) - u_n1
        return r

    def integrate(self):
        t = 0
        for n in range(self.t_steps-1):
            # print('Timestep {}'.format(n+1))
            if n % 5 == 0:
                self.array_data.emit(self.x_steps, self.y_steps, self.u[:, :, n])

            u_n = self.u[:, :, n].flatten()

            # Solve G for u_n1
            self.ae_solver.set_zStart(u_n)
            self.ae_solver.reInit()
            self.ae_solver.solve()

            u_n1 = self.ae_solver.z

            self.u[:, :, n+1] = np.reshape(u_n1, (self.y_steps, self.x_steps))

            self.current_status.emit(n+1, self.t_steps)
            if self.abort:
                t = n
                break
            t = n
        if t == self.t_steps-2:
            self.success_status.emit(True)
        if t != self.t_steps-2:
            self.success_status.emit(False)
        self.array_data.emit(self.x_steps, self.y_steps, self.u[:, :, t])


