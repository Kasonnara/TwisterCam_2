import generation_lib

# Angle de du manequin:
# Angle épaule gauche
aeg = -75
# Angle épaule droite
aed = -75
# Angle coude gauche
abg = -75
# Angle coude droit
abd = -75
# Angle cuisse gauche [5]
acg = 5
# Angle cuisse droite [5]
acd = 5
# Angle genou gauche [-5]
agg = -5
# Angle genou droit [-5]
agd = -5
# Angle de la tête [0]
at = 0
# Angle du buste [0]
ab = 0
# Rotation tout le corps [0]
a_full_body = 0
# Couleur de l'image finale [[1,1,1,1]]
color = [0, 0, 0, 1]
# Silouette pleine [False]
filled = False
# Epaisseur des silhouette si filled == False
epaisseur = 2

# edition des distances
#generation_lib.LONGUEUR_COU = 20

if __name__ == '__main__':
    generation_lib.pregen(aeg, aed, abg, abd, acg, acd, agg, agd, at, ab, flip, color, filled, epaisseur)
