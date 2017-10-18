import sys
import time
import threading

sys.path.append("./affichage_QT")
import affichage_QT as aqt
import Game_Core_2 as gc
import gameUI as gu


def init_full(config, env, dev_mode=False, **kwargs):
    if dev_mode:
        print(" |Initiate game data.")
    env, config = rebuild_interface(config=config, env=env, params=(("dev_mode",) if dev_mode else ()), verbose=dev_mode, **kwargs)
    env["silhouette_dict"] = env[
        "tc_win"].pose_widget.pose_dict  # TODO inverser, le cam win devrait reprendre les pose de l'env plutot que l'inverse
    env, config = reset_game(config=config, env=env, dev_mode=dev_mode, **kwargs)
    return env, config


def reset_game(config, env, dev_mode=False, **kwargs):
    # TODO move to GameCore
    if dev_mode:
        print(" |Initiate game status data.")
    env["life_values"] = [config.nbr_lifes for k in range(config.nbr_player)]
    env["tc_win"].s.set_lifes_alive.emit(env["life_values"])
    env["sequence"] = []  # TODO place sequence generation here
    env["current_validation"] = [False for k in range(config.nbr_player)]
    env["sequence_index"] = 0
    env["game_state"] = gc.GameState.HIDLE
    return env, config


def rebuild_interface(config=None, env=None, params=(), **kwargs):
    if params is None:
        return "rebuild_interface : reconstruit completement l'interface\n" \
               "    Utilisation:'rebuild_interface ['dev_mode']'"
    else:
        if "tc_win" in env.keys():
            last_tc_win = env["tc_win"]
        else:
            last_tc_win = None
        print(" |Build new graphical interface.")

        def validation_callback_proxy(player_id):
            gc.validate_player_pose(env, config, player_id)

        def exit_callback_proxy():
            env["game_state"] = gc.GameState.ENDING

        def play_callback_proxy():
            gc.play(env)

        env["tc_win"] = aqt.TwistCamWindow.TwistCamWindow("ressources/",
                                                          validation_callback_proxy,
                                                          exit_callback_proxy,
                                                          play_callback_proxy,
                                                          screen_id=config.screen_id,
                                                          nb_player=config.nbr_player,
                                                          nb_life=config.nbr_lifes,
                                                          timer_proportions=config.timer_proportions,
                                                          life_proportions=config.life_proportions,
                                                          player_proportions=config.player_proportions,
                                                          player_spacing_proportion=config.player_spacing_proportion,
                                                          border_proportion=config.border_marge_proportion,
                                                          multi_life_spacing_proportion=config.multi_life_spacing_proportion,
                                                          alpha_color=config.fond_vert_color,
                                                          validate_keys=config.validate_keys,
                                                          dev_mode="dev_mode" in params)
        env["tc_win"].pose_widget.show()
        if last_tc_win is not None:
            print(" |Delete old graphical interface.")
            last_tc_win.s.force_exit.emit()

    return env, config


if __name__ == '__main__':
    if "help" in sys.argv:
        print("Help not implemented yet!\n parameter possible:\n 'dev_mode' for all debug\n or 'dev_mode_g' for debugging graphical interface\n or 'dev_mode_c' for debugging core")  # TODO!!
        sys.exit(0)
    print("Starting TWISTERCAM")

    print("|Importing config file...")
    from TwistCamConf import TCConfig
    conf = TCConfig()

    print("|Initiating graphical interface...")
    env, _ = init_full(conf, {}, dev_mode=("dev_mode" in sys.argv or "dev_mode_g" in sys.argv))

    print("|Generating core thread...")
    c_thread = threading.Thread(target=gc.gamecore_thread,
                                args=(env, conf),
                                kwargs={"verbose": ("dev_mode" in sys.argv or "dev_mode_c" in sys.argv)})
    c_thread.setDaemon(True)
    c_thread.start()

    print("|Generating control thread...")
    terminal_thread = threading.Thread(target=gu.control_thread, args=(env, conf))
    terminal_thread.setDaemon(True)
    terminal_thread.start()

    # Start graphical interface, and restart it if it is rebuild
    while not env["game_state"] == gc.GameState.ENDING:
        env["tc_win"].main_app.exec_()
        print(" |Graphical interface exited.")
    print("#Graphical thread (main) exited.")
    # Extinction
    time.sleep(2)
    print("|                    Game made by Kasonnara, thanks for playing!")
    sys.exit(0)
