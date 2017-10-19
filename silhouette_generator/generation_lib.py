# coding=utf-8
import threading

import matplotlib.pyplot as plt
import numpy as np
from math import *

import time

"""taille de l'image de preview
(toutes les tailles suivantes doivent etres calculées relativement a celle ci)
"""
PREVIEW_X_SIZE = 160
PREVIEW_Y_SIZE = 110  # couper au buste : 110 , corps entier  : 190

"""Hauteur du nombril dans l'image (distance entre le nombril et le haut de l'image)"""
NOMBRIL_Y = 110

"""Tailles des parties du coprs"""
LARGEUR_CORPS = 20
LARGEUR_BRAS = 8
LARGEUR_TETE = 15
LARGEUR_JAMBE = 10

DEMI_LONGUEUR_BRAS = 25
LONGUEUR_BUSTE = 40
LONGUEUR_COU = 30
DEMI_LONGUEUR_JAMBE = 30

"""Couleur à utiliser pour l'image"""
COLOR = [1, 1, 1, 1]

"""Facteur multiplicatif de qualité de l'image final par rapport a la preview"""
PRECISION = 7


def new_image(hauteur, largeur):
    """ génère une nouvelle image vide et transparante de la taille demandée"""
    return np.zeros((hauteur, largeur, 4))


class Point:
    """Class basic de gestion de points"""

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def dist(self, p2):
        return dist(self, p2)


class Bone:
    """Classe pour gerer les os du squelette"""

    def __init__(self, ancre, longueur, largeur, angle, precision):
        """Cree basiquement un segment partant de l'ancre (qui peut etre soit un point soit un autre bone)
        de taille longueur et formant l'angle 'angle' avec l'os précédent s'il existe

        La structure contient aussi la largeur du membre qui sera utilisé pour le dessiner
        """
        self.ancre = ancre
        self.longueur = longueur * precision
        self.own_angle = angle / 180 * 3.14
        self.calculate_extremite()
        self.largeur = largeur * precision

    def get_angle(self):
        """renvoi l'angle absolu en radian de l'os"""
        if type(self.ancre) == type(self):
            return self.own_angle + self.ancre.get_angle()
        else:
            return self.own_angle

    def calculate_extremite(self):
        if type(self.ancre) == type(self):
            basepoint = self.ancre.get_extremite()
        else:
            basepoint = self.ancre
        a = self.get_angle()
        self.extremite = Point(basepoint.x - self.longueur * sin(a), basepoint.y - self.longueur * cos(a))

    def get_extremite(self):
        return self.extremite

    def dist(self, p):
        """Renvoi la distance entre le point et l'os"""
        if type(self.ancre) == type(self):
            return dist_point_seg(p, self.get_extremite(), self.ancre.get_extremite())
        else:
            return dist_point_seg(p, self.get_extremite(), self.ancre)


def dist(p1, p2):
    """renvoi la distance entre deux points"""
    return ((p2.x - p1.x) ** 2 + (p2.y - p1.y) ** 2) ** 0.5


def dist_point_seg(pp, pa, pb):
    """renvoi la distance d'un point a un segment"""
    t = ((pp.x - pa.x) * (pb.x - pa.x) + (pp.y - pa.y) * (pb.y - pa.y)) / dist(pa, pb) ** 2
    t = min(1, max(t, 0))
    projete = Point(pa.x + (pb.x - pa.x) * t, pa.y + (pb.y - pa.y) * t)
    return dist(pp, projete)


def check_epaisseur(dist_cible, dist_reel, epaisseur, trop_proche=False, trop_loin=True):
    """si l'epaisseur est positive renvoie deux booleans:
        le premier indique si la distance est trop proche pour etre dessinée
        le second indique si la sistance est trop lointaine pour etre dessinée
    :rtype bool, bool
    """
    if epaisseur > 0:
        return dist_cible - epaisseur > dist_reel or trop_proche, dist_reel > dist_cible and trop_loin
    else:
        return 0 > dist_reel or trop_proche, dist_reel > dist_cible and trop_loin


def generate_sil(a_epaule_gauche, a_epaule_droite, a_bras_gauche, a_bras_droite, a_cuisse_gauche=5, a_cuisse_droite=5,
                 a_genou_gauche=-5, a_genou_droit=-5, a_tete=0, a_body=0, flip=False, color=[0, 0, 1, 1], epaisseur=2,
                 precision=1, image_sil=None, verbose=True):
    """Trace sur imageSil la silouette
        paramètre :
            a_epaule_gauche : float, angle de l'epaule gauche de la silouette (en degré)
            a_epaule_droite: float, angle de l'epaule droite de la silouette (en degré)
            a_bras_gauche: float, angle du coude gauche de la silouette (en degré)
            a_bras_droite : float, angle du coude droit de la silouette (en degré)
            [color]: float[4] = COLOR, la couleur des pixels valides a colorier,
                sous la forme d'un tableau de 4 float (Rouge, vert bleu, alpha)
                chacun dans [0-1].
            [epaisseur]:float = 2, épaisseur du tracé (si negatif le figue sera pleine, sinon défini l'épaisseur du contour
            [precision]: float = 1, facteur d'agrandissment de l'image par rapport aux taille de la preview
            [image_sil]: float[PREVIEW_X_SIZE * precision][][4]= None, image de base auquel sera ajuté le nouveau tracé, si égale à None alors une nouvelle image vide sera crée
            :rtype: image

    """
    tailleY = round(PREVIEW_Y_SIZE * precision)
    tailleX = round(PREVIEW_X_SIZE * precision)

    epaisseur_reelle = epaisseur * precision
    # Corps
    pbc = Point(round(tailleX / 2), round(NOMBRIL_Y * precision))
    full_body_anchor = Bone(pbc, 1, 1, (180 if flip else 0), 1)  # utilisé pour orienter tout le corps
    bone_buste = Bone(full_body_anchor, LONGUEUR_BUSTE, LARGEUR_CORPS, a_body, precision)
    bone_epaule_gauche = Bone(bone_buste, LARGEUR_CORPS, LARGEUR_BRAS, 70, precision)
    bone_epaule_droite = Bone(bone_buste, LARGEUR_CORPS, LARGEUR_BRAS, -70, precision)
    bone_hanche_gauche = Bone(full_body_anchor, LARGEUR_CORPS / 1.5, LARGEUR_BRAS, 135, precision)
    bone_hanche_droite = Bone(full_body_anchor, LARGEUR_CORPS / 1.5, LARGEUR_BRAS, -135, precision)

    # Bras
    bone_bras_droit = Bone(bone_epaule_droite, DEMI_LONGUEUR_BRAS, LARGEUR_BRAS, -20 - a_epaule_droite, precision)
    bone_avant_bras_droit = Bone(bone_bras_droit, DEMI_LONGUEUR_BRAS, LARGEUR_BRAS, -a_bras_droite, precision)
    bone_bras_gauche = Bone(bone_epaule_gauche, DEMI_LONGUEUR_BRAS, LARGEUR_BRAS, 20 + a_epaule_gauche, precision)
    bone_avant_bras_gauche = Bone(bone_bras_gauche, DEMI_LONGUEUR_BRAS, LARGEUR_BRAS, a_bras_gauche, precision)

    # Jambes
    bone_cuisse_gauche = Bone(bone_hanche_gauche, DEMI_LONGUEUR_JAMBE, LARGEUR_JAMBE, 45 - a_cuisse_gauche, precision)
    bone_cuisse_droite = Bone(bone_hanche_droite, DEMI_LONGUEUR_JAMBE, LARGEUR_JAMBE, -45 + a_cuisse_droite, precision)
    bone_jambe_gauche = Bone(bone_cuisse_gauche, DEMI_LONGUEUR_JAMBE, LARGEUR_JAMBE, - a_genou_gauche, precision)
    bone_jambe_droite = Bone(bone_cuisse_droite, DEMI_LONGUEUR_JAMBE, LARGEUR_JAMBE, a_genou_droit, precision)

    # Os a prendre en compte pour la silhouette
    displayed_bone = []
    displayed_bone.append(bone_bras_droit)
    displayed_bone.append(bone_bras_gauche)
    displayed_bone.append(bone_avant_bras_droit)
    displayed_bone.append(bone_avant_bras_gauche)
    displayed_bone.append(bone_cuisse_droite)
    displayed_bone.append(bone_cuisse_gauche)
    displayed_bone.append(bone_jambe_droite)
    displayed_bone.append(bone_jambe_gauche)
    displayed_bone.append(bone_buste)

    # tete
    bone_cou = Bone(bone_buste, LONGUEUR_COU, LARGEUR_BRAS, a_tete, precision)
    p_tete = bone_cou.get_extremite()

    if image_sil is None:
        image_sil = new_image(tailleY, tailleX)
    for y in range(tailleY):
        for x in range(tailleX):
            p = Point(x, y)
            i = 0
            d_tete = dist(p, p_tete)
            trop_proche, trop_loin = check_epaisseur(LARGEUR_TETE * precision, d_tete, epaisseur_reelle)
            while (not trop_proche) and i < len(displayed_bone):
                d_reelle = displayed_bone[i].dist(p)
                trop_proche, trop_loin = check_epaisseur(displayed_bone[i].largeur, d_reelle,
                                                         epaisseur_reelle, trop_proche, trop_loin)
                i += 1
            if not (trop_loin or trop_proche):
                image_sil[y, x] = color[:]
        if y % 15 == 0 and verbose:
            print("avancement", round(y / tailleY * 100), "%")
    return image_sil;


def pregen(aeg, aed, abg, abd, acg=5, acd=5, agg=-5, agd=-5, at=0, ab=0, flip=False, color=[1, 1, 1, 1], filled=False,
           epaisseur=2):
    """Génère une preview de la silhouette, l'affiche
    et enfin demande si elle doit etre conservé
    auquelle cas une version HD est calculée et enregistrée
    dans le dossier 'generation_random'
    """
    plt.cla()
    preview_img = generate_sil(aeg, aed, abg, abd, acg, acd, agg, agd, at, ab, flip, color=[0, 0, 1, 1],
                               epaisseur=(-1 if filled else epaisseur), precision=1)
    plt.imshow(preview_img)
    plt.pause(0.5)
    print("Conserver l'image? ne rien taper pour passer, sinon entrez un nom")
    res = input()
    if not (res == ""):
        import random
        res = res + str(random.randint(0, 10000))
        print("Sauvegarde des preset de génération...")
        save_pregen_params(res, aeg, aed, abg, abd, acg, acd, agg, agd, at, ab, flip, color, filled, epaisseur)

        def HD_gen_thread(): #TODO Trop Shlaggggggg
            print("Génération de l'image HD en background (cela peut prendre quelques minutes)...")
            img = generate_sil(aeg, aed, abg, abd, acg, acd, agg, agd, at, ab, flip, color=color,
                               epaisseur=(-1 if filled else epaisseur), precision=PRECISION, verbose=False)
            print("Génération en background terminée, sauvegarde de l'image : generation_random/" + res + ".png")
            plt.imsave("generation_random/" + res + ".png", img)

        hd_thread = threading.Thread(target=HD_gen_thread)
        hd_thread.start()
        time.sleep(1)




def save_pregen_params(name, aeg, aed, abg, abd, acg, acd, agg, agd, at, ab, flip, color, filled,
                       epaisseur):
    with open("pregen.py.template", "r") as template:
        with open("pregen_param_saves/" + name + ".py", "w") as destination:
            s = ""
            for l in template:
                s += l
            r = s.format(*[aeg, aed, abg, abd, acg, acd, agg, agd, at, ab, flip, color, filled, epaisseur,
                     PREVIEW_X_SIZE, PREVIEW_Y_SIZE, NOMBRIL_Y, LARGEUR_CORPS, LARGEUR_BRAS, LARGEUR_TETE,
                     LARGEUR_JAMBE, DEMI_LONGUEUR_BRAS, LONGUEUR_BUSTE, LONGUEUR_COU, DEMI_LONGUEUR_JAMBE, PRECISION])
            destination.write(r)


if __name__ == '__main__':
    print("Ce module ne réalise rien de lui même utiliser plutot 'main_random.py'")
