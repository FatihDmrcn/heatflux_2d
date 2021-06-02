import PyQt5.QtWidgets as Qtw


class QHLine(Qtw.QFrame):
    def __init__(self):
        super().__init__()
        self.setFrameShape(Qtw.QFrame.HLine)
        self.setFrameShadow(Qtw.QFrame.Sunken)


class QVLine(Qtw.QFrame):
    def __init__(self):
        super().__init__()
        self.setFrameShape(Qtw.QFrame.VLine)
        self.setFrameShadow(Qtw.QFrame.Sunken)


class QSpacer(Qtw.QWidget):
    def __init__(self, policy_hor, policy_ver):
        super().__init__()
        self.setSizePolicy(policy_hor, policy_ver)
