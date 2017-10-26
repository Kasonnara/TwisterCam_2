import generation_lib

# Angle de du manequin:
# Angle épaule gauche
aeg = -70
# Angle épaule droite
aed = -100
# Angle coude gauche
abg = -10
# Angle coude droit
abd = 30
# Angle cuisse gauche [5]
acg = -90
# Angle cuisse droite [5]
acd = 0
# Angle genou gauche [-5]
agg = -45
# Angle genou droit [-5]
agd = 0
# Angle de la tête [0]
at = -50
# Angle du buste [0]
ab = 40
# Rotation tout le corps [0]
a_full_body = 0
# Mettre la silhouette de profile [False]
profile = True
# Couleur de l'image finale [[1,1,1,1]]
color = [0, 0, 0, 1]
# Silouette pleine [False]
filled = False
# Epaisseur des silhouette si filled == False
epaisseur = 2

# edition des distances
#generation_lib.LONGUEUR_COU = 20

if __name__ == '__main__':
    generation_lib.pregen(aeg, aed, abg, abd, acg, acd, agg, agd, at, ab, a_full_body, profile, color, filled, epaisseur)
