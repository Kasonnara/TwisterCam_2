import generation_lib

# Angle de du manequin:
# Angle épaule gauche
aeg = 55
# Angle épaule droite
aed = -60
# Angle coude gauche
abg = 85
# Angle coude droit
abd = -10
# Angle cuisse gauche [5]
acg = 20
# Angle cuisse droite [5]
acd = 20
# Angle genou gauche [-5]
agg = -20
# Angle genou droit [-5]
agd = 10
# Angle de la tête [0]
at = -5
# Angle du buste [0]
ab = 10
# Retourner tout le corps [False]
flip = False
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
