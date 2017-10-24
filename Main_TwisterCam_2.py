import sys
import threading
import time

import nc_control
sys.path.append("./affichage_QT")
import affichage_QT as aqt
import Game_Core_2 as gc
import gameUI as gu


def init_full(config, env, dev_mode=False, **kwargs):
    if dev_mode:
        print(" |Initiate game data.")
    rebuild_interface(config=config, env=env, params=(("dev_mode",) if dev_mode else ()), verbose=dev_mode, **kwargs)
    env["silhouette_dict"] = env[
        "tc_win"].pose_widget.pose_dict  # TODO inverser, le cam win devrait reprendre les pose de l'env plutot que l'inverse
    if dev_mode:
        print(" |Initiate game try data.")
    env["life_values"] = [config.nbr_lifes for k in range(config.nbr_player)]
    env["sequence"] = []
    env["current_validation"] = [False for k in range(config.nbr_player)]
    env["sequence_index"] = 0
    env["game_state"] = gc.GameState.IDLE


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
            if gc.play(env):
                print("   |GameCore, play command: OK, Starting Game.")
            else:
                print("   |GameCore, play command: Not ready, starting aborted.")

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
        print("Help not implemented yet!\n parameter possible:"
              "\n 'dev_mode' for all debug\n or 'dev_mode_g' for debugging graphical interface"
              "\n or 'dev_mode_c' for debugging core")  # TODO
        sys.exit(0)
    print("Starting TWISTERCAM")

    print("|Importing config file...")
    from TwistCamConf import TCConfig
    conf = TCConfig()

    print("|Initiating graphical interface...")
    env = {}
    init_full(conf, env, dev_mode=("dev_mode" in sys.argv or "dev_mode_g" in sys.argv))

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

    if conf.remote_control:
        print("|Start remote TCP control")
        tcp_thread = threading.Thread(target=nc_control.start_nc_receiver, args=(env, conf))
        tcp_thread.setDaemon(True)
        tcp_thread.start()
    else:
        print("|Remote TCP control is disabled")
    # Start graphical interface, and restart it if it is rebuild
    while not env["game_state"] == gc.GameState.ENDING:
        env["tc_win"].main_app.exec_()
        print(" |Graphical interface exited.")
    print("#Graphical thread (main) exited.")
    # Extinction
    time.sleep(2)
    print("|                    Game made by Kasonnara, thanks for playing!")
    sys.exit(0)
