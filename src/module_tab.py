import PyQt5.QtWidgets as Qtw
import PyQt5.QtCore as Qtc
import PyQt5.QtGui as Qtg
import numpy as np
import os
import datetime
from PIL import Image, ImageQt

from matplotlib import cm
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar


class QCanvas(FigureCanvas):
    def __init__(self, parent=None):
        fig = Figure()
        #self.ax = fig.add_subplot(111, projection='3d')
        self.ax = Axes3D(fig)
        super(QCanvas, self).__init__(fig)
        self.z_max = None
        self.z_min = None

    def set_lim(self, lower, upper):
        if lower == upper:
            self.z_min = 0
        if lower != upper:
            self.z_min = lower
        self.z_max = upper

    def plot(self, x_steps, y_steps, u):
        self.ax.clear()
        self.ax.set_zlim3d(self.z_min, self.z_max)
        self.ax.set_xlabel('x - Axis')
        self.ax.set_ylabel('y - Axis')
        self.ax.set_zlabel('Temperature')
        x = np.arange(0, x_steps, 1)
        y = np.arange(0, y_steps, 1)
        x, y = np.meshgrid(x, y)

        self.ax.plot_wireframe(x, y, u)
        self.draw()


class QDrawArray(Qtw.QWidget):
    def __init__(self, x_steps, y_steps, u):
        super().__init__()
        self.setMinimumSize(800, 600)
        self.image = None
        self.dy, self.dx = None, None
        self.x_steps, self.y_steps, self.u = x_steps, y_steps, u
        self.set_array(self.x_steps, self.y_steps, self.u)
        self.draw_grid = True

    def calculate_increments(self):
        self.dy = self.height()/(self.y_steps+2)
        self.dx = self.width()/(self.x_steps+2)

    def set_array(self, x_steps, y_steps, u):
        # Set increments
        self.x_steps = x_steps
        self.y_steps = y_steps
        self.calculate_increments()
        # Set image
        u = np.interp(u, (u.min(), u.max()), (0, 1))
        self.u = Image.fromarray(np.uint8(cm.coolwarm(u)*255)).convert('RGB')
        self.image = ImageQt.toqimage(self.u)
        self.repaint()

    def resizeEvent(self, event):
        self.calculate_increments()
        self.repaint()

    def paintEvent(self, event):
        painter = Qtg.QPainter()
        painter.begin(self)
        # Draw image
        rectangle_image = Qtc.QRectF(self.dx, self.dy, self.width()-2*self.dx, self.height()-2*self.dy)
        painter.drawImage(rectangle_image, self.image)
        # Draw dots
        pen = Qtg.QPen()
        pen.setColor(Qtc.Qt.black)
        pen.setJoinStyle(Qtc.Qt.MiterJoin)
        if self.draw_grid:
            # Draw points
            painter.save()
            pen.setWidth(3)
            painter.setPen(pen)
            for y in np.linspace(1.5*self.dy, self.height()-1.5*self.dy, self.y_steps):
                for x in np.linspace(1.5*self.dx, self.width()-1.5*self.dx, self.x_steps):
                    painter.drawPoint(x, y)
            painter.restore()
            # Draw lines
            painter.save()
            pen.setWidth(2)
            painter.setPen(pen)
            for y in np.linspace(self.dy, self.height()-self.dy, self.y_steps+1):
                start_point = Qtc.QPointF(self.dx, y)
                end_point = Qtc.QPointF(self.width()-self.dx, y)
                painter.drawLine(start_point, end_point)
            for x in np.linspace(self.dx, self.width()-self.dx, self.x_steps+1):
                start_point = Qtc.QPointF(x, self.dy)
                end_point = Qtc.QPointF(x, self.height()-self.dy)
                painter.drawLine(start_point, end_point)
            painter.restore()
        painter.end()


class QTabWindow(Qtw.QWidget):
    def __init__(self, *args):
        super().__init__()

        self.setSizePolicy(Qtw.QSizePolicy.Expanding, Qtw.QSizePolicy.Expanding)

        self.computed_arrays = []
        self.model_x = None
        self.model_y = None

        self.array = QDrawArray(*args)
        self.check_mesh = Qtw.QCheckBox('Show Grid')
        self.check_mesh.setChecked(True)
        self.check_mesh.clicked.connect(self.draw_mesh)

        self.plot = QCanvas(self)
        self.define_lim(args[2])
        self.plot.plot(*args)

        self.slider = Qtw.QSlider(Qtc.Qt.Horizontal)
        self.slider.valueChanged.connect(self.draw_array)
        self.slider.setSliderPosition(0)
        self.slider.setEnabled(False)

        self.frame_array = Qtw.QFrame()
        self.vbox_array = Qtw.QVBoxLayout()
        self.vbox_array.addWidget(self.array)
        self.vbox_array.addWidget(self.check_mesh)
        self.frame_array.setLayout(self.vbox_array)

        self.tab_widget = Qtw.QTabWidget()
        self.tab_widget.addTab(self.frame_array, "Array")
        self.tab_widget.addTab(self.plot, "3D-Plot")

        layout = Qtw.QVBoxLayout()
        layout.addWidget(self.tab_widget)
        layout.addWidget(self.slider)
        self.setLayout(layout)

    def define_lim(self, u):
        lower, upper = 0, 0
        if not self.computed_arrays:
            lower = np.amin(u)
            upper = np.amax(u)
        if self.computed_arrays:
            lower = np.amin(self.computed_arrays)
            upper = np.amax(self.computed_arrays)
        self.plot.set_lim(lower, upper)

    @Qtc.pyqtSlot()
    def delete_arrays(self):
        self.computed_arrays[:] = []
        self.slider.blockSignals(True)
        self.slider.setEnabled(False)
        self.slider.setSliderPosition(0)

    # Slot for step sizes so that array can be updated
    @Qtc.pyqtSlot(int, int, np.ndarray)
    def update(self, x, y, u):
        self.model_x = x
        self.model_y = y
        self.array.set_array(x, y, u)
        self.define_lim(u)
        self.plot.plot(x, y, u)

    @Qtc.pyqtSlot(int, int, np.ndarray)
    def save_array(self, x, y, u):
        if self.model_x is None or self.model_x is None:
            self.model_x = x
            self.model_y = y
        self.computed_arrays.append(u)

    @Qtc.pyqtSlot()
    def show_results(self):
        self.slider.blockSignals(False)
        self.slider.setEnabled(True)
        self.slider.setRange(0, len(self.computed_arrays) - 1)
        self.slider.setSliderPosition(self.slider.maximum())

    @Qtc.pyqtSlot(str)
    def save_results(self, directory):
        date = datetime.datetime.now()
        timestamp = date.strftime("%Y%m%d_%H%M")
        normpath = os.path.join(directory, timestamp)
        np.save(normpath, self.computed_arrays)

    def draw_array(self):
        self.array.set_array(self.model_x, self.model_y, self.computed_arrays[self.slider.sliderPosition()])
        self.define_lim(self.computed_arrays[self.slider.sliderPosition()])
        self.plot.plot(self.model_x, self.model_y, self.computed_arrays[self.slider.sliderPosition()])

    def draw_mesh(self):
        self.array.draw_grid = self.check_mesh.isChecked()
        self.array.repaint()
