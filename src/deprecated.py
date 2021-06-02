def integrate_deprecated(self):
        t = 0
        for n in range(self.t_steps-1):
            if n % 10 == 0:
                self.array_data.emit(self.x_steps, self.y_steps, self.u[:, :, n])
            for j in range(1, self.y_steps-1):
                for i in range(1, self.x_steps-1):
                    # Check whether internal model bc do exist
                    if self.bic[j][i] == 'F':
                        self.u[j][i][n+1] = self.u[j][i][n]*(1+self.gamma) + \
                                            self.alpha*(self.u[j][i-1][n] + self.u[j][i+1][n]) + \
                                            self.beta*(self.u[j-1][i][n] + self.u[j+1][i][n])
                    if self.bic[j][i] != 'F':
                        self.u[j][i][n+1] = self.u[j][i][n]
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

