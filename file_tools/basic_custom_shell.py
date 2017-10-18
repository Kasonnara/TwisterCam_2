#!bin /usr/bin/python3
import file_tools.auto_param_config as apc


def _show_dict(d, dict_name = None, tab_count = 3):
    """Affiche proprement un dictionnaire dans le terminal"""
    if not(dict_name == None):
        print("Show Dictionnaire",dict_name)
    for k in d.keys():
        print(" ",k, " "*(tab_count*4 - len(k)), "|", d[k])


##---------------------- COMMANDES DE BASE DU SHELL ---------------------------
def quit(env=None, params=[], **kwargs):
    if params == None:
        return "quit : arrete cette utilitaire\n    Utilisation:'quit'"
    elif not(env==None):
        env["stop"] = True
        return env, conf


def conf(env= None,config=None, params=[], **kwargs):
    if params == None :
        if config == None:
            return "conf : set n'importe quelle valeur de la config\n    Utilisation: IMPOSSIBLE PAS DE CONFIG DANS LE SHELL COURANT"
        else:
            return "conf : set n'importe quelle valeur de la config\n    Utilisation:'conf [key new_value]*'"
    elif config == None:
        print("ERREUR:Action impossible: le shell ne possède pas de config")
    elif params == []:
        s = "Config actuelle:\n"
        for key in config.__dict__.keys():
            s = s + " " + key + ":" + config.__dict__[key] + "\n"
        print(s)
        return None
    else:
        config.__dict__[params[0]] = params[1]
        return env, config


def help(env=None, config=None, params=[], commandes = [], alias = [], **kwargs):
    if params == None:
        return "help : affiche cette aide ou des info sur une commande\n    Utilisation : 'help' [-h|-d] [ ['conf'|'env'] [ -f func_name [-p param_name]* | attribut_name]* | commande_name]\n      help seul affiche la liste des commandes\n    '-d' [par defaut] affichera le resultat de cette fonction\n    '-h' affichera l'aide python sur le resultat de cette fonction\n     help + 'conf' affiche la liste des attribu de la config courante\n     help + 'conf' + a où a est une sequence de nom d'attibut et d'action d'exploration\n        ex : 'help conf truc -h -f get_machin -p chose bidule' executera help(conf['truc'].get_machin('chose').bidule)\n        -f permet de spécifier que le prochain paramètre est un appel de fonction\n       -p permet de spécifier que le prochain paramètre est un paramètre de la fonction\n    command_name : le nom d'une commande, l'aide de cette commande sera appalé comme avec 'help'"
    else:
        if params == []:
            print("Liste des commandes possibles:")
            for command_name in commandes.keys():
                if command_name == "default":
                    print("COMMANDE PAR DEFAUT (Executé si aucune commande n'est précisée)")
                print(commandes[command_name](env=env, config=config, params=None))
                print("    Alias:",*[a for a in alias.keys() if alias[a]==command_name])
        elif params[0] == "conf" or params[0] == "env":
            dict_analysed = config if params[0] == "conf" else env
            if len(params) == 1:
                _show_dict(dict_analysed, dict_name = "Configuration courante:" if params[0] == "conf" else "Environnement courant", tab_count = 6)
            else:
                print("Désolé pas encore implémenté") #TODO
        else:
            if params[0] in alias:
                params[0] = alias[params[0]]
            if params[0] in commandes:
                print(commandes[params[0]](env=env, config=config, params=None))
                print("    Alias:",*[a for a in alias.keys() if alias[a]==params[0]])

##----------------------- Liste des commandes de base -------------------------
default_commands = {"quit":quit, "set_conf":conf, "help":help}
default_alias={"set_configuration":"set_conf","setconf":"set_conf","exit":"quit","h":"help","aide":"help","fin":"quit"}

def shell(env, additionnal_command_dict, aliases={}, config = None, config_path = None, draw_func = None, shell_prompt = "basic_custom_shell >>>"):
    """Génère un shell console minimaliste.
    - env : dict = dictionnaire des variable d'environnement
    - additionnal_command_dict : dict = dictionnaire des commandes a ajouter au shell {command_name : function_to_execute}
    -[aliases]: dict = dictionnaire des alias '{alias : command_name}'
    -[config]: dict = un dictionnaire des variable d'environnement issues d'une config stockée en dur
    -[config_path]: string = le chemin d'accès a la config précedente
    -[draw_func]: une fonction qui sera executée entre chaque commande afin de redessinner le shell custom, la fonction prend en paramètre 2 dictionnaires (l'environnement et la config) et renvoi le string du prompt
    -[default_func]: un fonction qui sera executé si aucune commande n'est fournie
    -[shell_prompt]: String = le texte affiché a chaque prompt du shell.
    """
    env["stop"]=False
    env["config_path"] = config_path
    #global command_list
    command_list = default_commands.copy()
    command_list.update(additionnal_command_dict)
    #global alias_list
    alias_list = default_alias.copy()
    alias_list.update(aliases)
    while not(env["stop"]):
        if not(draw_func == None):
            shell_prompt = draw_func(env=env, config=config)
        input_entry = input(shell_prompt)
        commands = input_entry.split()
        # on sépare les différent argument ( séparés par des espace)
        if len(commands)> 0:
            command_found = False
            new_env_conf =  None
            if commands[0] in command_list.keys():
                command_found = True
                new_env_conf = command_list[commands[0]](env=env, config=config, params=commands[1:], commandes = command_list, alias = alias_list)
            elif commands[0] in alias_list.keys():
                command_found = True
                new_env_conf = command_list[alias_list[commands[0]]](env=env, config=config, params=commands[1:],commandes = command_list, alias = alias_list)
            if not(new_env_conf==None):
                new_env, new_config = new_env_conf
                # si la commande a retourné une config on l'applique
                if not(new_env == None):
                    env = new_env
                if not(new_config == None):
                    config = new_config
            if not command_found:
                print("Commande inconnue, RTFM ou Entrez 'help' pour afficher la liste des commandes")
        elif "default" in command_list.keys():
            command_list["default"](env=env, config=config, commandes =  command_list, alias = alias_list)
