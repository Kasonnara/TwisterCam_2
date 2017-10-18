"""Module content toutes les fonction de génération de séquence"""
import random


def Add_Random_Pose(nbr_poses, pose_dict, nbr_player, last_pose, delay):
    """appelé par Generate Sequence pour generer une sequance automatiquement
    Return une liste de nbr_pose élément contenant le nom d'une pose random
    Précondition, le nombre de poses disponnibles (de proba non nulle) doit etre > 1
    """
    result_seq = []
    variable_delay = delay + 0
    key_list = list(pose_dict.keys())
    while len(result_seq) < nbr_poses:
        n_pose = tuple(key_list[random.randint(0, len(key_list) - 1)] for k in range(nbr_player))
        validity = [(last_pose[k] == n_pose[k]
                     or pose_dict[n_pose[k]].proba < random.random()
                     or n_pose[k] == '')
                    for k in range(nbr_player)]
        if not any(validity):
            result_seq.append((n_pose, max(variable_delay, 2)))
            variable_delay = delay - 1
            last_pose = n_pose
            # TODO verifier que les pointeurs ne posent pas de problèmes en éditant le last_pose initial
        else:
            print("    |Sequence generation fail, retry.")
    return result_seq


def Generate_Sequence(generator_mode, nbr_poses, pose_dict, delay, nbr_player, start_pose="", start_delay=10):
    """ Génère une séquence de silouette issues de la liste fournies
     Deux silouette identique ne peuvent se suivres
     La séquence généré est ensuite enregistré dans l'environnement comme sequence courante afin de l'envoyer immédiatement sans la selectionner, et en dur dans le fichier de sequence temporaire

    PARAMS: - generator_mode : (random|select) = dans le premier cas la sequence sera automatiquement choisie au hasar
    dans le second cas une interface aider l'utilisateur a créer la séquence.
            - nbr_poses : integer = Le nombre de pose dans une séquence
            - Pose_dict : Pose dict = liste des Pose (images: silhouette/titre+proba)
            -[start_pose]: string = le nom de la pose de départ ou None

    RETURN tuple list = le liste des noms (clés du dictionnaire) silouettes choisies et le fond choisi
    Précond : nbr_poses > 0
    """
    result_seq = []
    if not (start_pose == None or start_pose == ""):
        result_seq.append(((start_pose,)*nbr_player, start_delay))
        nbr_poses -= 1
    if generator_mode == "random":
        print("   |Generating random sequence : lenght ", nbr_poses)
        result_seq = result_seq + Add_Random_Pose(nbr_poses, pose_dict, nbr_player,
                                                  (("" if len(result_seq) == 0 else result_seq[-1]),) * nbr_player, delay)
    elif generator_mode == "select":
        pass
        ## lancer un shell avec draw_func pour bien afficher la liste des poses disponnible et séléctionnées
    else:
        raise ValueError("Genrerate_Sequence : generate_mode inconnu :%s" % generator_mode)
    return result_seq