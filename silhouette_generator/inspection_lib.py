"""Ce module contient quelques outils pour verifier l'état des ressources utilisé
Entre autre permet de verifier que la couleur de fond utilisée pour le fond vert n'est jamais contenu dans les images"""

def Check_Background_Compatibility(image, background_color, precision=0.02):
    """Inspecte chaque pixel de l'image pour verifier qu'elle est compatible avec un fond vert
    de couleur background_color, c'est a dire qu'elle ne comporte aucun pixel de
    la même couleur a la précision près.
    PARAMS:
        - image : numpy_array une image numpy de matplotlib.image dont chaque case
        contient les données RVBA [0-1] d'un pixel de l'image
        - background_color : [[0-255]]^3 ou [0-1]^3 ou String
            = le triplet (r,v,b) ou r,v,b sont soit entier entre 0-255 soit des floatant entre 0-1
                soit un string représenant le code HTML equivalent en exadéciaml
        - precision : [0-1] ou [[0-255]] = un floatant entre 0-1 ou un entier entre 0-255
            représentant l'écart a la valeur background en dessous de laquel l'image est invalide
    RETURN: boolean
    """
    # TODO
    return False

def Full_Check_Background_Compatibilities(storage_directory, background_color, precision=0.02):
    """Inspecte tous les fichiers .png du dossier indiqué et renvoi d'une part
    la liste des noms de fichier compatibles avec le fond vert, et d'autre part
    la liste des noms de fichier non compatible avec le fond vert.
    PARAMS:
        - storage_directory : string = chemin du dossier d'image
        - background_color : [[0-255]]^3 ou [0-1]^3 ou String
            = le triplet (r,v,b) ou r,v,b sont soit entier entre 0-255 soit des floatant entre 0-1
                soit un string représenant le code HTML equivalent en exadéciaml
        - precision : [0-1] ou [[0-255]] = un floatant entre 0-1 ou un entier entre 0-255
            représentant l'écart a la valeur background en dessous de laquel l'image est invalide
    RETURN: string list, string list
    """
    # TODO
    return [], []

