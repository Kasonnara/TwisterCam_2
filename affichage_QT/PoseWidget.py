import os
import random
import time

from PyQt4 import QtGui
from PyQt4.QtCore import QSize, Qt, QRect
from PyQt4.QtGui import QPainter, QLabel, QPixmap, QColor

import file_tools.auto_param_config as apc


class Silhouette:
    """Gère l'image principale d'une pose"""

    def __init__(self, filename):
        self.filename = filename
        self.pixmap = QtGui.QPixmap(filename)


class Pose:
    def __init__(self, pose_manager, ressource_directory, pose_name, warnings_enabled=True, except_if_inexistant=False,
                 force_conf_generation=False):
        self.pose_manager = pose_manager
        self.pose_name = pose_name
        self.valide = False
        self.proba = 1
        if pose_name is None:
            self._init_empty(pose_manager, ressource_directory)
        else:
            self._load_pose(pose_manager, ressource_directory, pose_name, warnings_enabled=warnings_enabled,
                            except_if_inexistant=except_if_inexistant, force_conf_generation=force_conf_generation)

    def _load_pose(self, pose_manager, ressource_directory, pose_name, warnings_enabled=True,
                   except_if_inexistant=False, force_conf_generation=False):
        """Essai de charger l'image du fond
        précondition: les atttribus silhouette_widget et title_widget du Pose_Manager sont initialisés"""
        self.pose_name = pose_name
        silhouette_filename = ""
        # title_filename = ""
        # self.title = None
        self.sil = None
        # lire le fichier de conf
        conf_path = ressource_directory + "pose_configs/" + pose_name + ".conf"
        default_conf = {"pose_name": pose_name,
                        "silhouette_filename": "silhouette_storage" + os.sep + pose_name + ".png",
                        "title_filename": "title_storage" + os.sep + pose_name + "_title.png", "proba": 1}
        conf_data = apc.text_conf_param(default_conf, conf_path, warnings_enabled=warnings_enabled, verbose=False,
                                        rewrite_conf_when_fail=force_conf_generation)

        if conf_data is None or conf_data == {}:
            # Erreur de lecture de la config
            if warnings_enabled:
                print("Warning! fichier de conf de la pose inexistant (", pose_name + ".conf", ")")
            if except_if_inexistant:
                # retourner une erreur
                raise ValueError("Fichier de conf de pose inexistant")
        else:
            silhouette_filename = ressource_directory + conf_data["silhouette_filename"]
            # title_filename = ressource_directory + conf_data["title_filename"]
            self.pose_name = conf_data["pose_name"]
            self.proba = conf_data["proba"]

        if os.access(silhouette_filename, os.R_OK):
            self.sil = Silhouette(silhouette_filename)
            self.valide = True
        # self.title = Title(title_filename, pose_name)
        # self.title.adjust_size(pose_manager.title_widget.width(), pose_manager.title_widget.height())

    def _init_empty(self, pose_manager, ressource_directory, warnings_enabled=True, except_if_inexistant=False):
        #self.title = Title(ressource_directory + "vide.png", "")
        self.sil = Silhouette(ressource_directory + "vide.png")
        self.valide = True
        self.pose_name = ""
        self.proba = 0

    def get_silhouette(self):
        return self.sil


class PoseWidget(QLabel):
    def __init__(self, ressource_directory, dim: QSize, player_size: QSize, player_ratio_spacing: float=0.33,
                 alpha_color="#FF00FF", vertical_random_ratio=0.1, toggle_period=0.2,
                 player_colors = ("#FF0000", "#8904B1", "#FF8000", "#01DFD7", "#0404B4"),
                 key_press_event_callback=None,
                 dev_mode=False):
        """
        :param ressource_directory: String, chemin du dossier ressource.
        :param dim: QSize, taille alloué au widget.
        :param dev_mode: boolean [facultatif (defaut False)], active le mode developpement.
        """
        # Setup widget
        super().__init__()
        if dev_mode:
            self.setStyleSheet("background-color:blue")
        else:
            self.setStyleSheet("background-color:" + alpha_color)
        self.setMaximumSize(dim)
        self.setMinimumSize(dim)

        # Init constant for toggling
        self.toggle_period = toggle_period
        self.toggle_state = 0
        self.default_colors = tuple(QColor(c) for c in player_colors)
        self.toggle_colors = list([[QColor(c) for c in player_colors], [QColor(c) for c in player_colors]])
        self.toggle_cache_pixmap = list([QPixmap(dim), QPixmap(dim)])
        self.alpha_color = alpha_color

        # Setup poses
        self.current_silhouette = None
        self.player_rect = QRect((dim.width() - player_size.width()) * 0.5,
                                 (dim.height() - player_size.height()) * 0.5,
                                 player_size.width(),
                                 player_size.height())
        self.player_ratio_spacing = player_ratio_spacing
        self.vertical_random_ratio = vertical_random_ratio
        self.player_pixel_spacing = 0
        self.pose_dict = {}
        self.vertical_random = ()
        self.order = ()
        self._load_all_poses(ressource_directory, load_all_images=True, verbose=False,
                             filter_valid=True, dev_mode=dev_mode)

        # Init constant for pose drawing
        exemple_sil_pixmap = self.pose_dict[list(self.pose_dict.keys())[1]].get_silhouette().pixmap
        vertical_scale = self.player_rect.height() / exemple_sil_pixmap.height()
        self.pose_hauteur = round(exemple_sil_pixmap.height() * vertical_scale)
        self.pose_largeur = round(exemple_sil_pixmap.width() * vertical_scale)
        self.player_pixel_spacing = self.player_ratio_spacing * self.pose_largeur

        # Event callback
        self.key_press_event_callback = key_press_event_callback

    def _load_all_poses(self, ressource_directory, load_all_images=False, verbose=False,
                        filter_valid=True, dev_mode=False):
        """Essai de charger toutes les poses ayant un fichier de conf dans le sous-dossier 'pose_configs' du dossier
        ressource fourni
        PARAMS: - ressource_directory : path-like = le chemin du dossier de ressource du jeu
                -[load_all_images]: boolean = [False] si True les images (.png/.jpg) présentent dans le dossiers
                'silhouette_storage' mais ne comportant pas de ficher de conf associées seront aussi chargées et une
                configuration automatique leur sera créé.
                -[verbose]: boolean = [False] si True, la liste des fonds trouvés sera affichée ainsi que leur validité
                (contient tous les fonds valides où non)
                -[filter_valid]: boolean = [True] si True seul les fonds correctment chargés seront revoyés.
        Postcondition : le dictionnaire pose_dict des fonds est chargé"""
        if dev_mode:
            print("   Loading Poses...", end="")
        self.pose_dict = {}
        # lister tous les nom de poses (c'est a dire tous les fichier d'extension '.conf' du dossier
        # background_storage en coupant l'extension en question)
        name_list_c = [path[:-5] for path in os.listdir(ressource_directory + "pose_configs") if
                       path.find(".conf") > -1]
        # Tenter de charger tous les poses listées
        for pose_name in name_list_c:
            self.pose_dict[pose_name] = Pose(self, ressource_directory, pose_name, force_conf_generation=False)
            if verbose:
                print("Loading pose", pose_name, "from config; succès :", self.pose_dict[pose_name].valide)

        # ajouter les nom des fichers .png si l'option est activée, en évitant les doublons
        if load_all_images:
            name_list_i = [path[:-4] for path in os.listdir(ressource_directory + "silhouette_storage") if
                           path.find(".png") > -1 and not (path[:-4] in name_list_c)]
            # Tenter de charger tous les fond listées en générant toujours les config
            for pose_name in name_list_i:
                self.pose_dict[pose_name] = Pose(self, ressource_directory, pose_name, except_if_inexistant=False,
                                                 force_conf_generation=True)
                if verbose:
                    print("Loading background", pose_name, "from image; succès :", self.pose_dict[pose_name].valide)
        # ajout de l'image vide
        self.pose_dict[""] = Pose(self, ressource_directory, None, except_if_inexistant=True,
                                  force_conf_generation=False)
        if filter_valid:
            r_list = []
            for pose_name in self.pose_dict.keys():
                if not self.pose_dict[pose_name].valide:
                    r_list.append(pose_name)
            for r_pose_name in r_list:
                self.pose_dict.pop(r_pose_name, None)

        if dev_mode:
            print("OK")

    def set_poses(self, pose_names):
        """Set la pose affichée à l'écran enla designant par son nom"""
        self.current_silhouette = ()
        for pose_name in pose_names:
            if pose_name in self.pose_dict.keys():
                self.current_silhouette = self.current_silhouette + \
                                          (self.pose_dict[pose_name].get_silhouette(),)
            else:
                print("Warning: Set_Pose d'une pose inconnue :", pose_name)
        self.toggle_colors = [list(self.default_colors), list(self.default_colors)]
        n = len(self.current_silhouette)
        self.order = random.sample(range(n), n)
        self.vertical_random = tuple(self.vertical_random_ratio * self.pose_hauteur * random.random() for k in self.default_colors)
        self.repaint_poses(0)
        self.repaint_poses(1)
        self.toggle_color()

    def toggle_color(self):
        self.toggle_state = (self.toggle_state + 1) % 2
        self.setPixmap(self.toggle_cache_pixmap[self.toggle_state])

    def repaint_poses(self, toggle_index):
        painter = QPainter(self.toggle_cache_pixmap[toggle_index])
        #painter.eraseRect(self.rect())
        painter.fillRect(self.rect(), QColor(self.alpha_color))

        if self.current_silhouette is not None:

            left_center = self.player_rect.left() + 0.5 * self.player_rect.width() - self.player_pixel_spacing * (
                len(self.current_silhouette) - 1) * 0.5

            for k in self.order:
                new_pixmap = QPixmap(self.pose_largeur, self.pose_hauteur)
                new_pixmap.fill(self.toggle_colors[toggle_index][k])
                new_pixmap.setMask(self.current_silhouette[k].pixmap.scaled(self.pose_largeur, self.pose_hauteur).mask())
                painter.drawPixmap(int(left_center + k * self.player_pixel_spacing - (self.pose_largeur * 0.5)),
                                   self.player_rect.top() + self.vertical_random[k],
                                   self.pose_largeur,
                                   self.pose_hauteur,
                                   new_pixmap)
        painter.end()

    def keyPressEvent(self, e):
        self.key_press_event_callback(e)


def color_switching(tc_win, player_id, new_HTML_color, duration):
    if duration > 0:
        new_color = QColor(new_HTML_color)
        tc_win.pose_widget.toggle_colors[0][player_id] = new_color
        tc_win.s.repaint_poses.emit(0)
        time.sleep(duration)
        tc_win.pose_widget.toggle_colors[1][player_id] = new_color
        tc_win.s.repaint_poses.emit(1)


if __name__ == "__main__":
    print("PoseWidget test start...")
    import sys
    for size in [(1200, 600), (100, 200), (600, 100)]:
        for k in range(2, 6):
            main_app = QtGui.QApplication(sys.argv)
            ressources = "../ressources/"
            main_window = PoseWidget(ressources,
                                     QSize(size[0], size[1]),
                                     QSize(size[0], size[1]/(k*0.5)),
                                     dev_mode=False)
            print("Test des poses :", list(main_window.pose_dict.keys())[1:k])
            main_window.set_poses(list(main_window.pose_dict.keys())[1:k])
            main_window.setWindowTitle("Test PoseWidget")
            main_window.show()
            main_app.exec_()
            del main_app
    print("PoseWidget test finished.")
    sys.exit()
