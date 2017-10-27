import time

import file_tools.basic_custom_shell as bcs
import Game_Core_2 as gc
from Main_TwisterCam_2 import rebuild_interface
import Sequence_Generator as sg


def control_thread(env, conf):
    print(" |Initiate game shell.")
    # commandes spéciales du shell
    commandes = {"gen_seq": call_gen_seq, "play": start_game, "preview": start_preview,
                 "rebuild_interface": rebuild_interface}
    # aliases du shell
    aliases = {"generate_sequence": "gen_seq", "new_seq": "gen_seq", "new": "gen_seq", "view": "preview",
               "start": "play"}
    time.sleep(1)
    print(" |Start TwisterCam command shell")
    bcs.shell(env, commandes, aliases=aliases, config=conf, shell_prompt="TwisterCam >>>")
    # Terminaison du programme
    env["tc_win"].s.force_exit.emit()
    print("#Control thread exited.")


def start_preview(config=None, env=None, params=[], **kwargs):
    return start_game(config=config, env=env, params=params, preview=True, **kwargs)


def start_game(config=None, env=None, params=[], preview=False, **kwargs):
    if params is None:
        if preview:
            return "preview : passe le shell en mode préview, qui affichera la prochaine séquence et de nouvelle " \
                   "commande pour les modifications temporaire de la conf (reglage des images (taille et offset), etc) "
        else:
            return "play : passe le shell directement en mode jeu, le mode preview permet de passer en " \
                   "mode jeu avec plus de possibilité de réglage "
    else:
        print("  |Starting a game...")
        if gc.reset_game(env, config):
            if preview:
                Start_interface_preview(config=config, env=env, params=params, **kwargs)
            else:
                Start_interface_cam(config=config, env=env, params=params, **kwargs)
        else:
            print("Erreur pas de séquence disponnible")
        return env, config


def call_gen_seq(config=None, env=None, params=[], **kwargs):
        """ Fonction respectant le standard des commande de mon shell custom
        Permet de générer une sequence manuellement, avec des paramètres spéciaux
        Trèspeu utilisé en pratique"""
        if params == None:
            return "gen_seq : utilitaire de génération de sequences" \
                   "\n  Permet de génerer namuellement des séquences custom, mais peut utile, en pratique." \
                   "\n    Utilisation:'gen_seq [nbr_pose [mode [type]]]'\n      nbr_pose : integer >0, le nombre de pose de la séquence;  default: valeur de la config a la clé 'nbr_poses'\n      mode : (random|select), le mode de création de la séquence; default: valeur de la config a la clé 'generator_mode'\n      type : (anime|fixe|mur), le type de séquence;  default: valeur de la config a la clé 'sequence_type'"
        else:
            # lancer la fonction en donnant priorité aux paramètres facultatif, et a la config en deuxième recours
            result = sg.Generate_Sequence(params[2] if len(params) > 1 else config.generator_mode,
                                          params[1] if len(params) > 0 else config.nbr_poses,
                                          env["silhouette_dict"],
                                          config.pose_delay,
                                          config.nbr_player,
                                          start_pose=config.start_pose,
                                          max_difficulty_level=env["tc_win"].pose_widget.max_difficulty_level)
            # enregistrer le result dans l'env s'il est fructueux
            if not (result == None or len(result[0]) == 0):
                print("    |Génération Réussie.")
            else:
                print("    |Sequence generation failed.")


# --------------------------------Commandes active pendant le mode préview -----------------------------
def toggle_next_pose(env=None, params=[], verbose=False, **kwargs):
    if params is None:
        return "next_pose : passe a la pose suivante et redéssine l'affichage, aucune vie n'est perdu, on peut donc " \
               "considérer que si n = 1 la pose est validée\n    Utilisation : 'next_pose [n]'\n      n : le nombre " \
               "de poses a passer par défaut[1] "
    else:
        n = 1 if len(params) == 0 or not (params[0].isdecimal()) else int(params[0])
        gc.toggle_next_pose(env=env, n=n, verbose=verbose)


def toggle_previous_pose(env=None, params=[], verbose=False, **kwargs):
    if params is None:
        return "previous_pose : remonte a la pose précédente et redéssine l'affichage\n    Utilisation : " \
               "'previous_pose [n]'\n      n : le nombre de poses a passer "
    else:
        n = -1 if len(params) == 0 or not (params[0].isdecimal()) else -int(params[0])
        gc.toggle_next_pose(env=env, n=n, verbose=verbose)


preview_commandes = {"next_pose": toggle_next_pose, "previous_pose": toggle_previous_pose}
preview_aliases = {"n": "next_pose", "p": "previous_pose"}


def Start_interface_preview(config=None, env=None, params=[], **kwargs):
    """Passe le programme en mode préview: initialise l'affichage pré-view et un nouveau shell avec de nouvelles
    commandes adaptées prend le relais toute modification de la config pendant ce mode pourra etre reporté sur la
    config principale en répondant "yes" lors du prompt de sortie.
    """
    if params is None:
        return "preview : lance le mode préview sur la séquence courante\n    Utilisation : 'preview [key value]*'\n " \
               "     [key value] est une liste de couple où key est la clé d'un paramètre de la config, et value la " \
               "valeur a lui assigner le temps de la préview "
    else:
        loc_conf = config.copy()
        print("   |----- Passage en mode 'Preview' -----")
        env["game_state"] = gc.GameState.PREVIEW
        bcs.shell(env, preview_commandes, aliases=preview_aliases, config=loc_conf, config_path=env["config_path"],
                  shell_prompt="TwisterCam [preview] >>>")
        print("   |-----  Sortie du mode 'Preview' -----")
        env["stop"] = False
        env["game_state"] = gc.GameState.IDLE
        print("Voulez vous lancer le jeu avec cette configuration?[y/n] >>> ")
        reponse = input()
        if reponse == "y" or reponse == "o" or reponse.find("yes") > -1 or reponse.find("oui") > (-1):
            Start_interface_cam(config=loc_conf, env=env, params=[])
        print("Voulez vous conserver cet nouvelle configuration? [y/n] >>>")
        reponse = input()
        if reponse == "y" or reponse == "o" or reponse.find("yes") > -1 or reponse.find("oui") > -1:
            return env, loc_conf
        else:
            return None


# --------------------------------Commandes actives pendant l'execution du jeu---------------------------
def play(env=None, params=None, **kwargs):
    if params is None:
        return "play : met le jeu en mode marche, à activer une fois que TVn7 affiche le jeu à l'écran pour lancer " \
               "les chrono\n    Utilisation : 'play' "
    else:
        gc.play(env)


def break_game(env=None, params=None, **kwargs):
    if params is None:
        return "stop : met le jeu en mode pause, a priori pas besoin, sauf si necessité absolu pour pépin technique " \
               "\n    Utilisation : 'stop' "
    else:
        if gc.end_game(env):
            print("    |GamCore: End of game requested.\nNow, you can use 'reload', when TVn7 cut the game .")
        else:
            print("    |GamCore: Current state incompatible for ending.")


def reload(env=None, config=None, params=None, **kwargs):
    if params is None:
        return "reload : re-initialise l'état du jeu pour une nouvelle partie identique" \
               "\n    Ne sort pas du mode jeu contrairement à exit." \
               "\n    Utilisation : 'reload' "
    else:
        if gc.reset_game(env, config):
            print("    |GamCore: reload game requested.\nNow you can use 'play' when TVn7 show the game.")
        else:
            print("    |GamCore: Current state incompatible for reloading.")


cam_commandes = {"play": play, "break": break_game, "default": toggle_next_pose, "reload": reload}
cam_aliases = {"k": "break", "stop": "break", "p": "play", "n": "default", "v": "default", "next_pose": "default"}


def Start_interface_cam(config=None, env=None, params=[], **kwargs):
    """Passe le programme en mode execution du jeu: initialise l'affichage réel du jeu et un nouveau shell avec de
    nouvelles commandes adaptées prend le relais toute modification de la config pendant ce mode est temporaire,
    sauf si elle est réecrite en dur sur le disque, dans touts les cas a la sortie du mode la configuration 'vivante'
    reprend son ancienne valeure
    """
    if params is None:
        return "play : lance le mode d'execution du jeu sur la séquence courante\n    Utilisation : 'play [key " \
               "value]*'\n      [key value] est une liste de couple où key est la clé d'un paramètre de la config, " \
               "et value la valeur à lui assigner le temps de la sequence "
    else:
        loc_conf = config.copy()
        print("   |===== Passage en mode 'Jeu' =====")
        bcs.shell(env, cam_commandes, aliases=cam_aliases, config=loc_conf, config_path=env["config_path"],
                  shell_prompt="TwisterCam [jeu] >>>")
        env["game_state"] = gc.GameState.IDLE
        env["stop"] = False
        print("   |=====  Sortie du mode 'Jeu' =====")
