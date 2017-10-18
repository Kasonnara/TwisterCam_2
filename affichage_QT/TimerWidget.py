from PyQt4 import QtGui
from PyQt4.QtCore import QSize
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QLabel


class TimerWidget(QLabel):
    def __init__(self,ressource_directory, dim: QSize, clock_dim_ratio: tuple=(0.9, 0.35), clock_color="#FFFFFF", dev_mode=False):
        super().__init__()
        self.setMaximumSize(dim)
        self.setMinimumSize(dim)
        self.font_color = clock_color
        # Setup clock background
        self._load_timer_picture(ressource_directory)
        #self.setPixmap(self.fond_pixmap.scaled(dim, Qt.KeepAspectRatio))
        self.setPixmap(self.fond_pixmap.scaled(QSize(dim.width()-5,dim.height()-5), Qt.KeepAspectRatio))
        self.setContentsMargins((dim.width() - self.pixmap().width()) * 0.5,
                                (dim.height() - self.pixmap().height()) * 0.5,
                                (dim.width() - self.pixmap().width()) * 0.5,
                                (dim.height() - self.pixmap().height()) * 0.5)
        if dev_mode:
            self.setStyleSheet("background-color:yellow")
        else:
            self.setAttribute(Qt.WA_TranslucentBackground, True)
        # Setup clock foreground
        self.clock_layout = QtGui.QGridLayout()
        self.setLayout(self.clock_layout)
        self.clock_layout.setContentsMargins(0,0,0,0)
        self.clock_label = QLabel()
        self.clock_layout.addWidget(self.clock_label)
        self.clock_label.setAlignment(Qt.AlignCenter)
        #self.default_font = self.font() #TODO set custom font
        font = self.clock_label.font()
        font.setBold(True)
        self.clock_label.setFont(font)
        bound = self.clock_label.fontMetrics().boundingRect("00")
        font_size_ratio = min(dim.width() * clock_dim_ratio[0] / bound.width() * 0.5,
                              dim.height() * clock_dim_ratio[1] / bound.height())
        font.setPointSizeF(font_size_ratio * self.clock_label.font().pointSize()+10)
        self.clock_label.setFont(font)
        self.clock_label.setAttribute(Qt.WA_TranslucentBackground, True)
        self.set_timer_value(0)

    # TODO def adjustSize , to resize the widget

    def set_timer_value(self, new_val):
        self.clock_label.setText("<font color=" + self.font_color + ">" + str(new_val) + "</font>")

    def _load_timer_picture(self, ressource_directory):
        """Load les Pixelmap des images du timer
        Utile a l'initialisation """
        # Image de fond
        self.fond_pixmap = QtGui.QPixmap(ressource_directory + "fond_timer.png")


if __name__ == "__main__":
    print("TimerWidget test start...")
    import sys
    for size in [(300, 300), (100, 200), (600, 100)]:
        for k in [0, 5, 10, 42]:
            main_app = QtGui.QApplication(sys.argv)
            ressources = "../ressources/"
            main_window = TimerWidget(ressources,
                                      QSize(size[0], size[1]),
                                      dev_mode=False)
            main_window.set_timer_value(k)
            main_window.setWindowTitle("Test TimerWidget")
            main_window.show()
            main_app.exec_()
            del main_app
    print("TimerWidget test finished.")
    sys.exit()