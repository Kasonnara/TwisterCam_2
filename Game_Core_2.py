import threading
import time
from enum import Enum

from PoseWidget import color_switching
from TwistCamConf import TCConfig
from Sequence_Generator import Generate_Sequence


def gamecore_thread(env, config: TCConfig, verbose=False, dt=0.2):
    env["timer_value"] = config.start_pose_delay
    last_rounded_timer_value = 0
    while not (env["game_state"] == GameState.ENDING):
        while env["game_state"] == GameState.PLAYING or env["game_state"] == GameState.WAIT_PLAY:
            if env["sequence"] is None or len(env["sequence"]) <= env["sequence_index"]:
                end_game(env, config)
                raise ValueError("Not normal ending!")
            if env["timer_value"] < 0:
                if config.timer_mode == TimerMode.EACH_POSE:
                    if verbose:
                        print("    |GameCore, time-up : remaining people %s lose 1 life." %
                              [k for k in range(config.nbr_player) if not env["current_validation"][k]])
                    end_round(env, config)
                elif config.timer_mode == TimerMode.FULL_GAME:
                    if verbose:
                        print("    |GameCore, time-up : everyone lose.")
                    env["life_values"] = [0] * config.nbr_player
                    env["tc_win"].s.set_lifes_alive.emit(env["life_values"])
                    end_game(env, config)
            else:
                # continue game sequence
                if env["game_state"] == GameState.PLAYING and not env["timer_mode"] == TimerMode.DISABLED:
                    env["tc_win"].s.toggle_color.emit()
                    env["timer_value"] -= dt
                    if not last_rounded_timer_value == round(env["timer_value"]):
                        last_rounded_timer_value = round(env["timer_value"])
                        env["tc_win"].s.set_timer.emit(str(last_rounded_timer_value))
                        print("    |GameCore, timer changed : %d" % (last_rounded_timer_value))
            time.sleep(dt)
        time.sleep(0.5)
    print("#Core thread exited.")


def play(env):
    if env["game_state"] == GameState.WAIT_PLAY:
        env["game_state"] = GameState.PLAYING
        return True
    else:
        return False


def validate_player_pose(env, config, player_id):
    if (env["game_state"] == GameState.PREVIEW \
       or env["game_state"] == GameState.PLAYING)\
       and env["timer_mode"] is not TimerMode.DISABLED:
        if not env["current_validation"][player_id]:
            env["current_validation"][player_id] = True
            print("    |Validation. state:%s" % env["current_validation"])
            green_switching_thread = threading.Thread(target=color_switching,
                                                      args=(env["tc_win"], player_id, "#FFFFFF", config.animation_delay))
            green_switching_thread.start()
            if env["current_validation"].count(False) <= 1:
                end_round(env, config)
        else:
            print("Player %d is already validated!" % player_id)
    else:
        print("Validation refused, game state (%s) invalid for this action." % env["game_state"])


def end_round(env, config):
    env["timer_mode"] = TimerMode.DISABLED
    for k in range(config.nbr_player):
        if not env["current_validation"][k]:
            env["life_values"][k] -= 1
            red_switching_thread = threading.Thread(target=color_switching,
                                                    args=(env["tc_win"], k, "#D00000", config.animation_delay))
            red_switching_thread.start()
    env["tc_win"].s.set_lifes_alive.emit(env["life_values"])
    for k in range(round(config.animation_delay / 0.2)):
        env["tc_win"].s.toggle_color.emit()
        time.sleep(0.2)
    toggle_next_pose(env=env, config=config)


def toggle_next_pose(env=None, config=None, n=1, **kwargs):
    env["sequence_index"] = env["sequence_index"] + n
    env["current_validation"] = [env["life_values"][k] <= 0 for k in range(config.nbr_player)]
    if env["sequence_index"] < len(env["sequence"]):
        alive_array = [env["life_values"][k] > 0 for k in range(config.nbr_player)]
        if alive_array.count(True) > 1:
            next_poses = env["sequence"][env["sequence_index"]][0]
            # hide eliminated players
            next_poses = tuple(pose if env["life_values"][k] > 0 else "" for k, pose in enumerate(next_poses))
            env["tc_win"].s.set_poses.emit(next_poses)
            env["tc_win"].s.set_poses_visibility.emit(tuple(not v for v in env["current_validation"]))
            # reset timer if necessary
            if config.timer_mode == TimerMode.EACH_POSE:
                env["timer_value"] = env["sequence"][env["sequence_index"]][1]
                env["tc_win"].s.set_timer.emit(str(env["timer_value"]))
            print("    |GameCore, switch next pose", env["sequence"][env["sequence_index"]][0])
            # Restart timer
            env["timer_mode"] = config.timer_mode
        else:
            if alive_array.count(True) == 0:
                end_game(env, config)
            else:
                end_game(env, config, winner=alive_array.index(True))
    else:
        end_game(env, config)


def end_game(env, config, winner=None):
    if env["game_state"] == GameState.WAIT_PLAY or env["game_state"] == GameState.PLAYING:
        env["game_state"] = GameState.WAIT_RELOAD
        env["timer_mode"] = TimerMode.DISABLED
        env["sequence"] = None

        # Display ending feedback
        env["tc_win"].s.set_timer.emit("^^")
        if winner is not None:
            threading.Thread(target=execute_win_animation, args=(env, config, winner)).start()
        else:
            time.sleep(1)
        # Stop all display
        env["tc_win"].s.set_poses.emit(tuple("" for k in range(config.nbr_player)))
        env["tc_win"].s.set_poses_visibility.emit(tuple(False for k in range(config.nbr_player)))

        print("    |GameCore, Game ended!")
        return True
    else:
        return False


def execute_win_animation(env, config, winner_id):
    env["tc_win"].s.set_poses_visibility.emit(tuple(k==winner_id for k in range(config.nbr_player)))
    for p in config.wi_seq[1]:
        env["tc_win"].s.set_poses.emit(tuple(p if k==winner_id else "" for k in range(config.nbr_player)))
        time.sleep(config.wi_seq[0])




def reset_game(env, config):
    if env["game_state"] == GameState.IDLE or env["game_state"] == GameState.WAIT_RELOAD:
        env["life_values"] = [config.nbr_lifes for k in range(config.nbr_player)]
        env["tc_win"].s.set_lifes_alive.emit(env["life_values"])
        env["current_validation"] = [False for k in range(config.nbr_player)]
        env["sequence_index"] = 0
        env["timer_mode"] = config.timer_mode
        # try generate env["sequence"] if it doesn't exist yet
        if check_seq_exist(env, config):
            env["tc_win"].s.set_poses.emit(env['sequence'][0][0])
            env["timer_value"] = config.start_pose_delay
            env["tc_win"].s.set_timer.emit(str(env["timer_value"])) # TODO correct pose delai
            env["game_state"] = GameState.WAIT_PLAY
            return True
    return False


def check_seq_exist(env, config):
    # Check if sequence already exist
    if env["sequence"] is None or len(env["sequence"]) == 0:
        # Select generation mode, TODO add other modes
        if config.generator_mode == "random":
            # mode random donc on génère une sequence a la volé
            env["sequence"] = Generate_Sequence(config.generator_mode,
                                                config.nbr_poses,
                                                env["silhouette_dict"],
                                                config.pose_delay,
                                                config.nbr_player,
                                                start_pose=config.start_pose)
    if not (env["sequence"] == None or len(env["sequence"]) == 0):
        print("    |Séquence OK.")
        return True
    else:
        print("Impossible de démarrer le jeu, aucune sequence n'est définie.")
        return False


class GameState(Enum):
    IDLE = 0  # application dans son état initial, attend une commande pour agir
    PREVIEW = 1  # mode préview, affiché en condition réelle (coté TVn7)
    PREVIEW_HIDE = 2  # mode préview affiché coté net7
    WAIT_PLAY = 3  # partie prête, attend seulement la top départ.
    PLAYING = 4  # partie en cours d'execution
    WAIT_RELOAD = 5  # partie terminé attend que TVn7 change d'écran pour revenir en HIDLE
    ENDING = 6  # Toute l'application doit s'arreter.


class TimerMode(Enum):
    DISABLED = 0  # pas de timer
    FULL_GAME = 1  # One timer for the full game, if it reach 0 every one lose
    EACH_POSE = 2  # The timer is reset for every poses.


if __name__ == '__main__':
    print("Ce module ne fait rien seul, veuillez utiliser Main_TwisterCam.py ")

