import os
import threading
from threading import Thread

from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineReceiver
import twisted
from twisted.internet import reactor

import Game_Core_2

player_allocation = None

class NcReceiver(LineReceiver):
    def __init__(self, env, config):
        self.thread = None # For ensuring to not lose messages. TODO
        self.env = env # for calling validation
        self.config = config # for calling calidation
        self.allocation = None # id of the player affected to the TCP connexion

    def connectionMade(self):
        print("Connection made.")
        global player_allocation
        try:
            self.allocation = player_allocation.index(False)
            player_allocation[self.allocation] = True
            self.send_str(("Connexion établie\n" +
                           "Vous controlez le %de joueur (en partant de la gauche)\n" +
                           "Entrez 'h' pour l'aide")
                          % (self.allocation+1,))
            print("Connexion établie, pour manager le joueur %d" % (self.allocation+1,))
        except ValueError:
            print("Too much TCP connexion, not enough players!")
            self.send_str("Too much TCP connexion, not enough players!")
            self.transport.loseConnection()

    def dataReceived(self, data:str):
        #print("Receved data from player %d :%s" %(self.allocation, data))
        if data.startswith(b"p"):
            print("Remote play command")
            if Game_Core_2.play(self.env):
                self.send_str("Game started")
            else:
                self.send_str(
                    "Current game state (%s) is not compatible with 'play' command." % (self.env["game_state"],))
        elif data.startswith(b"k"):
            if Game_Core_2.end_game(self.env):
                self.send_str("Game stopped")
            else:
                self.send_str(
                    "Current game state (%s) is not compatible with 'break' command." % (self.env["game_state"],))
        elif data.startswith(b"s"):
            global player_allocation
            self.send_str("Game state:%s\n%d/%d moderateur connected." %
                          (self.env["game_state"], player_allocation.count(True), len(player_allocation)))
        elif data.startswith(b"r"):
            if Game_Core_2.reset_game(self.env, self.config):
                self.send_str("Game reloaded")
            else:
                self.send_str(
                    "Current game state (%s) is not compatible with 'reset' command." % (self.env["game_state"],))

        elif data.startswith(b"h"):
            self.send_str("Le premier caractère de chaque message envoyé est inspecté \n" +
                          "et interprété s'il correspond à l'une des commandes suivantes:\n" +
                          "p : play \n" +
                          "k : break\n" +
                          "s : status\n" +
                          "r : reload\n" +
                          "h : help \n" +
                          "Sinon le message sera interprété comme une validation.")

        else:
            validation_thread = threading.Thread(target=Game_Core_2.validate_player_pose,
                                                 args=(self.env, self.config, self.allocation))
            validation_thread.setDaemon(True)
            validation_thread.start()
            self.send_str("Validation reçue.")

    def connectionLost(self, reason):
        if self.allocation is not None:
            print("Connection lost with player %d manager. Reason : %s" % (self.allocation + 1, reason))
            global player_allocation
            player_allocation[self.allocation] = False

    def send_str(self, s, end='\n'):
        """Wrapper for having a print equivalent user side."""
        self.transport.write(''.join((s, end)).encode())


class ValiderFactory(Factory):
    def __init__(self, env, config):
        self.env = env
        self.config = config

    def buildProtocol(self, addr):
        return NcReceiver(self.env, self.config)

def print_own_ip():
    # TRÈS TRÈS MOCHE, non portable TODO remake
    s = os.system("ip a | grep 'inet ' | grep 'wlan'")


def start_nc_receiver(env, config, port=1117):
    global player_allocation
    player_allocation = [False] * config.nbr_player
    # Init listening
    endpoint = TCP4ServerEndpoint(reactor, port)
    endpoint.listen(ValiderFactory(env, config))
    print("Run tcp listener on port %d,\nip:" % (port,), end="")
    print_own_ip()
    reactor.run(installSignalHandlers=0)
    print("TCP Receiver exited.")

