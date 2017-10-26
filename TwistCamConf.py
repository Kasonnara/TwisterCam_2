class TCConfig:
    def __init__(self):
        # Modes possibles : random  (pour une génération automatique)
        self.generator_mode = "random"

        # Conf de la couleur du fond vert utilisé par TVn7 (HTML color)
        self.fond_vert_color = "00FF00"

        # Nombre de vie par joueur.
        self.nbr_lifes = 3
        self.life_enabled = True

        # Nombre de pose par séquence.
        self.nbr_poses = 12

        # Nombre de joueur dans la partie.
        self.nbr_player = 4

        # Nom de la 1e pose.
        # Si défini, la première pose d'une séquence sera toujour celle-ci
        self.start_pose = ""

        # Délais entre chaque pose
        self.pose_delay = 5

        # Délais spécial pour la 1e pose.
        self.start_pose_delay = 7

        # delai des animation de reussite/echec
        self.animation_delay = 2

        # Séquence executé quand un joueur gagne la partie, (intervale entre chaque image, liste des images)
        self.wi_seq = (0.3, ["Strong8080", "standup8888"]*6 + ["holla25310","holla18516", "holla25310", "holla31916", "holla46043", "holla52584", "holla46043", "holla31916"]*2)

        # ------------ Gestion de L'INTERFACE --------------
        # L'identifiant de l'écran a utiliser, a priori -1, testez différentes valeur si le dimensionnement de l'interface est raté.
        self.screen_id = -1

        # Ecart minimal entre l'interface et le bord de l'écran
        # Valeurs dans [0 .. 1] (1 équivaut a la largeur de l'écran)
        self.border_marge_proportion = 0.03
        # Taille (horizontal, vertical) du chronomètre
        # Valeurs dans [0 .. 1] (1 équivaut a la largeur de l'écran)
        self.timer_proportions = (0.14, 0.25)
        # Taille des barre de vie de chauqe joueur
        # Valeurs dans [0 .. 1] (1 équivaut a la largeur de l'écran)(RQ la donnée horizontal est ingorée en multijoueur)
        self.life_proportions = (0.5, 0.15)
        # Taille des silhouette de chauqe joueur
        # Valeurs dans [0 .. 1] (1 équivaut a la largeur de l'écran)
        self.player_proportions = (1, 0.7)
        # Écart entre chaque joueur
        # /!\ dans [0 .. 1] (1 équivaut à la largeur D'UN JOUEUR !!)
        self.player_spacing_proportion = 0.25
        # Écart entre chaque barre de vie en mode multiplayer
        # /!\ dans [0 .. 1] (1 équivaut à la largeur D'UN JOUEUR !!)
        self.multi_life_spacing_proportion = 0.10
        # Mode de fonctionnement du timer (FULL_GAME | EACH_POSE | DISABLED)
        # FULL_GAME : means 1 timer for the full sequence.
        # EACH_POSE : means the timer is reset with each pose.
        # DISABLED  : no timer.
        from Game_Core_2 import TimerMode
        self.timer_mode = TimerMode.EACH_POSE

        # Touche du clavier a utiliser pour valider les différents joueurs
        self.validate_keys = (65, 32, 16777220, 43) # keys : 'a', 'space', 'enter', '+'
        # Enable remote control with tcp connexions
        self.remote_control = True

    def copy(self):
        # DO NOT EDIT
        new_conf = TCConfig()
        new_conf.__dict__ = self.__dict__.copy()
        return new_conf
