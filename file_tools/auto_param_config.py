#! /bin/usr/python3

"""Module de récupération des paramètres bash"""
import sys
import os
def dict_param(default_dict, warnings_enabled= True, verbose = False):
    """ récupère les paramètres bash préfixés d'une clé correspondant au clés du dictionnaire des valeurs par défauts
        Sauf pour les boolean pour lesquel il n'est pas forcement nécessaire de préciser la valeur, une simple ecriture de la clé les met a true
    PARAMS:
        - default_dict : dict = de dictionnaire des valeur par défaut a renvoyer
        -[warnings_enabled]: bool = a deactiver pour ne pas afficher de warning en cas deparamètre non reconu
        -[verbose]: bool = a activer pour afficher le detail des opérations effectuées
    précond : tous les variables du dictionnaire doivent pouvoir etre contruites par un appel de leur constructeur avec un string en paramètre
                    (c.a.d que tous les types utilisés doivent posseder un constructeur uniaire prenant en paramètre un le string donné en paramètre)
              les clés du dictionnaire sont des string
    Result:
        un dictionnaire ayant les même clé que le dict par défaut et pour valeur les valeur indiqué en paramètre (ou les valeurs par défaut sinon)

    """
    # récupération des argument donnés en bash
    return dict_param_manuel(default_dict, sys.argv[1:], warnings_enabled=warnings_enabled, verbose=verbose)

def dict_param_manuel(default_dict, params, warnings_enabled= True, verbose = False):
    """idem que dict_param sauf que la liste des key/value est en paramètre plutôt que les param"""
    # init des variables / constantes
    default_options = default_dict.keys()
    result = default_dict.copy()
    current_option_key = None

    for param in params:
        if param in default_options:
            if verbose:
                print("Auto_Param_Config : Option detectée \"" + str(param) + "\"")
            current_option_key = param
            if type(default_dict[param])==type(True):
                # cas exeptionnel des boolean qui peut etre mis a true simplement en donnant la clé
                result[param] = True
                if verbose :
                    print(" Type boolean identifié, Passage a True par defaut de",param)
        elif not(current_option_key == None):
            result[current_option_key] = type(default_dict[current_option_key])(param)
            if verbose :
                print("Auto_Param_Config : valeur =", params)
            current_option_key = None
        elif param == "-h" or param =="help" or param =="--help":
            print("Auto-generate help:")
            print("Lors de l'execution dans un terminal, vous pouvez redéfinir tous les paramètre ci-dessous en suivant le format suivant comme paramètre de la commande de lancement du programme")
            print("Format : 'option_name   value_to_set'")
            print("    Seule exeption : pour les booleans, il est possible de les passer à True simplement en donnant l'option")
            print("Options possibles : ")
            for key in default_options:
                print("  Option:",key,", Type:",type(default_dict[key]),", Default value:",default_dict[key])
            print("\nAppuillez sur 'Entrée' pour continuer...")
            input()
        else:
            # le param fournit n'est pas reconu comme une option key et n'est pas précédé d'une option key
            if warnings_enabled:
                print("WARNING : Auto_Param_Config : paramètre innutilisé",params)
            current_option_key = None
    return result


def text_conf_param(default_dict, conf_path , warnings_enabled= True, verbose = False, rewrite_conf_when_fail=True):
    """ récupère les paramètres de configuration enregistré dans un fichier de conf.
        Un dictionnaire des valeurs par défauts peut etre fournit, les valeur manquantes seront ajoutées au fichier de conf
        Tous les types utilisés doivent avoir un sérialiseur (str) et un constructeur désérialiser

        le fichier de config s'écrit avec les consigne suivante:
            un '#' passe toute la fin de la ligne en commentaire_index
            un paramètre suit le format : '[key_name]=key_value' suivi d'une fin de ligne
            il n'est pas garantit que les texte qui ne sont ni des commentaire ni des paramètre soit conservés
    PARAMS:
        - default_dict : dict = de dictionnaire des valeur par défaut a renvoyer
        - conf_path : String = le chemin d'accès au fichier de config
        -[warnings_enabled]: bool = a deactiver pour ne pas afficher de warning en cas deparamètre non reconu
        -[verbose]: bool = a activer pour afficher le detail des opérations effectuées
        -[rewrite_conf_when_fail] : bool = si True (default) en cas d'échec de la lecture de la conf elle est réécrite
    précond : tous les variables du dictionnaire doivent pouvoir etre contruites par un appel de leur constructeur avec un string en paramètre
                    (c.a.d que tous les types utilisés doivent posseder un constructeur uniaire prenant en paramètre un le string donné en paramètre)
              les clés du dictionnaire sont des string
    Result:
        un dictionnaire ayant les même clé que le dict par défaut et pour valeur les valeur indiqué en conf (ou les valeurs par défaut sinon)
    """
    result = {}
    if os.access(conf_path, os.R_OK):
        conf_file = open(conf_path,"r")
        if conf_file:
            for ligne in conf_file:
                commentaire_index = ligne.find("#")
                commentaire = ligne[commentaire_index:]
                data = ligne[:commentaire_index]
                key_start = data.find("[")
                key_end = data.find("]=")
                if not(key_start == -1 or key_end==-1):
                    # les marqueur existent donc on extrait la clé et la valeure
                    key = data[key_start+1:key_end]
                    value = data[key_end+2:]
                    if key in default_dict.keys():
                        if value == "":
                            value = None
                        else:
                            value = type(default_dict[key])(value)
                        # si une valeur par defaut existe on adapte le type de la valeur trouvé
                    result[key]=value
            conf_file.close()
    if not(result == {}) or rewrite_conf_when_fail:
        if verbose:
            print("apc | completion auto de la config")
        # ajout des champ du default dict qui n'existent pas dans la config
        conf_file_completion = open(conf_path,"a")
        if conf_file_completion:
            for key in default_dict.keys():
                if not(key in result.keys()):
                    result[key]=default_dict[key]
                    conf_file_completion.write("\n# -- Auto-generate-conf {0}\n[{0}]={1}\n#".format(key, default_dict[key]))
            conf_file_completion.close()
    return result

def write_text_conf(new_config, path, error_enabled= True, verbose = False):
    """ Procedure qui ecrit sur le disque la configuration donnée en paramètre.
        Tous les types utilisés doivent avoir un sérialiseur (str) et un constructeur désérialiser

        le fichier de config s'écrit avec les consigne suivante:
            un '#' passe toute la fin de la ligne en commentaire_index
            un paramètre suit le format : '[key_name]=key_value' suivi d'une fin de ligne
            il n'est pas garantit que les texte qui ne sont ni des commentaire ni des paramètre soit conservés
    PARAMS:
        - new_config : dict = de dictionnaire des valeur par défaut a renvoyer
        - conf_path : String = le chemin d'accès au fichier de config
        -[warnings_enabled]: bool = a deactiver pour ne pas afficher de warning en cas deparamètre non reconu
        -[verbose]: bool = a activer pour afficher le detail des opérations effectuées
    précond : tous les variables du dictionnaire doivent pouvoir etre contruites par un appel de leur constructeur avec un string en paramètre
                    (c.a.d que tous les types utilisés doivent posseder un constructeur uniaire prenant en paramètre un le string donné en paramètre)
              les clés du dictionnaire sont des string
    Result:
        un dictionnaire ayant les même clé que le dict par défaut et pour valeur les valeur indiqué en conf (ou les valeurs par défaut sinon)
    """
    found_key = []
    output = []
    if os.access(path, os.R_OK):
        conf_file = open(path,"r")
        if conf_file:
            for ligne in conf_file:
                commentaire_index = ligne.find("#")
                commentaire = ligne[commentaire_index:]
                data = ligne[:commentaire_index]
                key_start = data.find("[")
                key_end = data.find("]=")
                if not(key_start == -1 or key_end==-1):
                    # les marqueur existent donc on extrait la clé et la valeure
                    key = data[key_start+1:key_end]
                    value = data[key_end+2:]
                    if key in new_config.keys():
                        if verbose:
                            print("config write : found key:",key)
                        found_key.append(key)
                        output.append("["+key+"]="+("" if new_config[key] ==  None else str(new_config[key]))+commentaire)
                    else:
                        output.append(ligne)
            conf_file.close()
    if os.access(path, os.W_OK):
        if verbose and (len(found_key) < len(new_config.keys())):
            print("apc | completion write de la config")
        conf_file_completion = open(path,"w")
        # Recopie des champ préexistants
        for l in output:
            conf_file_completion.write(l+"\n")
        # ajout des champ de la config qui n'existent pas encore
        if conf_file_completion:
            for key in new_config.keys():
                if not(key in found_keys):
                    if verbose:
                        print("config write :  add key :",key)
                    conf_file_completion.write("\n# -- Auto-generate-conf {0}\n[{0}]={1}\n#".format(key, new_config[key]))
            conf_file_completion.close()
    else:
        print("Impossible d'écrire la config!")
        if error_enabled:
            raise ValueError("Impossible d'écrire la config")
