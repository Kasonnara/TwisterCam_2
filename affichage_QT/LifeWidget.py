import math
from PyQt4 import QtGui
from PyQt4.QtCore import QSize
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QLabel


class LifeWidget(QLabel):
    DEFAULT_FUCKING_MARGIN = 9

    def __init__(self, ressource_directory, dim: QSize, nbr_life, dev_mode=False):
        """
        Generate a Widget displaying lifes.
        :param ressource_directory: String, the path to ressource directory
        :param dim: QtCore.QSize, the dimension of the space allocated to LifeWidget.
        :param nbr_life: int, the number of heart to display.
        :param dev_mode: boolean [Facultative (default False)], if True debug informations are displayed.
        """
        super().__init__()
        self.setMaximumSize(dim)
        self.setMinimumSize(dim)
        self._load_life_picture(ressource_directory)
        # Setup grid layout
        self.main_grid_layout = QtGui.QGridLayout(self)
        ratio_h_w = (dim.height() * self.life_picture.width()) / (dim.width() * self.life_picture.height())
        self.nbr_columns = math.ceil((nbr_life / ratio_h_w) ** 0.5)
        self.nbr_lines = math.ceil(nbr_life / self.nbr_columns)
        self.column_size = dim.width() / self.nbr_columns
        self.line_size = dim.height() / self.nbr_lines
        self.main_grid_layout.setSpacing(0)
        # Resize pictures
        self.life_picture = self.life_picture.scaled(self.line_size,
                                                     self.column_size, Qt.KeepAspectRatio)
        self.dead_picture = self.dead_picture.scaled(self.line_size,
                                                     self.column_size, Qt.KeepAspectRatio)
        # Setup heart images
        self.life_labels = []
        for k in range(nbr_life):
            self.life_labels.append(QtGui.QLabel())
            self.main_grid_layout.addWidget(self.life_labels[-1], k//self.nbr_columns, k % self.nbr_columns)
            if dev_mode:
                self.life_labels[-1].setStyleSheet("background-color:pink")
        if dev_mode:
            self.setStyleSheet("background-color:purple")
            print("LifeWidget Dimensions:\n | screen_size : %s, %s\n | ratio : %s \n | lines : %s\n | rows : %s" % (
                dim.height(), dim.width(), ratio_h_w, self.nbr_lines, self.nbr_columns))
        # Adjust border for centering
        horizontal_space = dim.width() - self.life_picture.width() * self.nbr_columns
        vertical_space = dim.height() - self.life_picture.height() * self.nbr_lines
        self.setContentsMargins(math.floor(horizontal_space * 0.5 - self.DEFAULT_FUCKING_MARGIN),
                                math.ceil(vertical_space*0.5 - self.DEFAULT_FUCKING_MARGIN),
                                math.ceil(horizontal_space*0.5 - self.DEFAULT_FUCKING_MARGIN),
                                math.floor(vertical_space*0.5 - self.DEFAULT_FUCKING_MARGIN))
        self.set_alive(0)

    # TODO def adjustSize , to resize the widget

    def _load_life_picture(self, ressource_directory):
        """Load les Pixelmap des images des vies
        Utile a l'initialisation"""
        self.life_picture = QtGui.QPixmap(ressource_directory + "life.png")
        self.dead_picture = QtGui.QPixmap(ressource_directory + "dead.png")

    def set_alive(self, nbr_alive):
        """
        Set labels 'dead' or 'alive'.
        :param nbr_alive: int, number of labels to set as 'dead'.
        :return: None
        """
        #TODO tout passer en positif!
        for i, label in enumerate(self.life_labels):
            label.setPixmap(self.life_picture if i < nbr_alive else self.dead_picture)

    def setVisibleKeepingSpace(self, new_state: bool):
        """
        Show/Hide all life labels but unlike setVisible, the widget keep allocating space.
        :param new_state: boolean, the new state of visibility.
        :return: None
        """
        for label in self.life_labels:
            label.setVisible(new_state)


if __name__ == "__main__":
    print("LifeWidget test start...")
    import sys
    import time
    for size in [(300, 200), (100,200)]:
        for k in range(1, 15):
            main_app = QtGui.QApplication(sys.argv)
            ressources = "../ressources/"
            main_window = LifeWidget(ressources,
                                     QSize(size[0], size[1]),
                                     k, dev_mode=True)
            main_window.setWindowTitle("Test LifeWidget")
            main_window.set_alive(1)
            main_window.show()
            main_app.exec_()
            del(main_app)
    print("LifeWidget test finished.")
    sys.exit()