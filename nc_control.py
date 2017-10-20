import threading
from threading import Thread

from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineReceiver
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
            self.send_str("Connexion établie\nVous controlez le %de joueur (en partant de la gauche)"
                          % (self.allocation+1,))
        except ValueError:
            print("Too much TCP connexion, not enough players!")
            self.send_str("Too much TCP connexion, not enough players!")
            self.transport.loseConnection()

    def dataReceived(self, data):
        print("Receved data from player %d :%s" %(self.allocation, data))
        validation_thread = threading.Thread(target=Game_Core_2.validate_player_pose,
                                             args=(self.env, self.config, self.allocation))
        validation_thread.setDaemon(True)
        validation_thread.start()
        self.send_str("Validation reçue.")

    def connectionLost(self, reason):
        print("Connection lost with player %d manager." % (self.allocation + 1,))
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


def start_nc_receiver(env, config, port=2222):
    global player_allocation
    player_allocation = [False] * config.nbr_player
    # Init listening
    endpoint = TCP4ServerEndpoint(reactor, port)
    endpoint.listen(ValiderFactory(env, config))
    reactor.run(installSignalHandlers=0)
    print("TCP Receiver exited.")

