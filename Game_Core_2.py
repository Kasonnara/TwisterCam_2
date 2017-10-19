import threading
import time
from enum import Enum

from PoseWidget import color_switching
from TwistCamConf import TCConfig


def gamecore_thread(env, config: TCConfig, verbose=False, dt=0.2):
    env["timer_value"] = config.start_pose_delay
    last_rounded_timer_value = 0
    while not (env["game_state"] == GameState.ENDING):
        while env["game_state"] == GameState.PLAYING or env["game_state"] == GameState.WAIT_PLAY:
            if env["sequence"] is None or len(env["sequence"]) <= env["sequence_index"]:
                end_game(env, verbose=verbose)
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
                    end_game(env, verbose=verbose)
            else:
                # continue game sequence
                if env["game_state"] == GameState.PLAYING and not config.timer_mode == TimerMode.DISABLED:
                    env["tc_win"].s.toggle_color.emit()
                    env["timer_value"] -= dt
                    if not last_rounded_timer_value == round(env["timer_value"]):
                        last_rounded_timer_value = round(env["timer_value"])
                        env["tc_win"].s.set_timer.emit(last_rounded_timer_value)
                        print("    |GameCore, timer changed : %d" % (last_rounded_timer_value))
            time.sleep(dt)
        time.sleep(0.5)
    # Exit program
    print("#Core thread exited.")


def play(env):
    if env["game_state"] == GameState.WAIT_PLAY:
        print("   |GameCore, Starting Game.")
        env["game_state"] = GameState.PLAYING
    else:
        print("   |GameCore, Not ready, starting aborted.")


def validate_player_pose(env, config, player_id):
    if env["game_state"] == GameState.PREVIEW \
       or env["game_state"] == GameState.PLAYING:
        env["current_validation"][player_id] = True
        print("    |Validation. state:%s" % env["current_validation"])
        if config.animation_delay > 0:
            green_switching_thread = threading.Thread(target=color_switching,
                                                      args=(env["tc_win"], player_id, "#05FF05", "#FFFFFF", 0.2, config.animation_delay))
            green_switching_thread.start()
        if env["current_validation"].count(False) < 1:
            end_round(env, config)
    else:
        print("Validation refused, game state (%s) invalid for this action." % env["game_state"])


def end_round(env, config):
    for k in range(config.nbr_player):
        if not env["current_validation"][k]:
            env["life_values"][k] -= 1
            # TODO animate red silhouette
    env["tc_win"].s.set_lifes_alive.emit(env["life_values"])
    initial_TM, config.timer_mode = config.timer_mode, TimerMode.DISABLED
    time.sleep(config.animation_delay)
    config.timer_mode = initial_TM
    toggle_next_pose(env=env, config=config)


def toggle_next_pose(env=None, config=None, n=1, **kwargs):
    env["sequence_index"] = env["sequence_index"] + n
    env["current_validation"] = [env["life_values"][k] < 0 for k in range(config.nbr_player)]
    if env["sequence_index"] < len(env["sequence"]) \
        and any(env["life_values"][k]>0 for k in range(config.nbr_player)):
        next_poses = env["sequence"][env["sequence_index"]][0]
        # hide eliminated players
        next_poses = tuple(pose if env["life_values"][k] > 0 else "" for k,pose in enumerate(next_poses))
        env["tc_win"].s.set_poses.emit(next_poses)
        if config.timer_mode == TimerMode.EACH_POSE:
            env["timer_value"] = env["sequence"][env["sequence_index"]][1]
            env["tc_win"].s.set_timer.emit(int(env["timer_value"]))
        print("    |GameCore, switch next pose", env["sequence"][env["sequence_index"]][0])
    else:
        end_game(env, config)


def end_game(env, config, **kwargs):
    print("    |GamCore: End of game requested.")
    env["game_state"] = GameState.WAIT_RELOAD


class GameState(Enum):
    HIDLE = 0  # application dans son état initial, attend une commande pour agir
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
