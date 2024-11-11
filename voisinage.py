import numpy as np
import init_sol
import time

# implémente les algorithmes de recherche locale.
# Les différentes parties:
    # Les fonctions d'évaluation des voisins et de changement de solution.
    # Les fonctions pour une étape de la recherche locale (montee/descente)
    # Les fonctions de recherche locale à appeler

# *****************************************************************************************************************
# Fonctions de changement de solution et d'évaluation de voisin
# L'évaluation des voisins se fait en temps constant car on garde en mémoire les capacités résiduelles.
# *****************************************************************************************************************


def reaffectation_1tache(pb, delta_f,j,t):
    # reaffectation de la tache t a l'agent j
    # nouvelle valeur de la fonction objectif
    pb.f = pb.f + delta_f
    # maj des capcitées résiduelles 
    pb.b_res[pb.x[t]]  = pb.b_res[pb.x[t]] + pb.r[pb.x[t],t]
    pb.b_res[j] = pb.b_res[j] - pb.r[j,t]
    # affectation
    ancien_agent = pb.x[t]
    pb.x[t] = j
    return ancien_agent

def cout_reaffectation_1tache(pb, j,t):
    # calcul de réalisabilité et de la variation de la valeur pour une reaffectation de la tache t a l'agent j
    delta_f = - pb.c[pb.x[t],t] + pb.c[j,t]
    realisable =(pb.b_res[j] - pb.r[j,t] >= 0)
    return realisable, delta_f
    
def swap_taches(pb, delta_f, t1,t2):
    # permutation des agents pour deux taches.
    # nouvelle valeur de la fonction objectif
    pb.f = pb.f + delta_f
    # maj des capacités résiduelles
    pb.b_res[pb.x[t2]] = pb.b_res[pb.x[t2]] + pb.r[pb.x[t2],t2] - pb.r[pb.x[t2], t1]
    pb.b_res[pb.x[t1]] = pb.b_res[pb.x[t1]] + pb.r[pb.x[t1],t1] - pb.r[pb.x[t1], t2]
    # swap des taches
    i1 = pb.x[t1]
    pb.x[t1] = pb.x[t2]
    pb.x[t2] = i1
    pass

def cout_swap_taches(pb,t1,t2):
    # calcul de la réasibilité et de la variation de valeur pour une permutation des tâches 
    delta_f = - pb.c[pb.x[t1],t1] - pb.c[pb.x[t2],t2] + pb.c[pb.x[t2],t1] + pb.c[pb.x[t1],t2]
    realisable =(pb.b_res[pb.x[t1]] - pb.r[pb.x[t1],t2] + pb.r[pb.x[t1],t1]>= 0) and (pb.b_res[pb.x[t2]] - pb.r[pb.x[t2],t1]+ pb.r[pb.x[t2],t2] >= 0)
    return realisable, delta_f

# *****************************************************************************************************************
# Fonctions pour une étape de recherche locale.
# Pour les deux voisinages considéres : montée et descente.
# *****************************************************************************************************************


def montee_un_pas_swap(pb):
    """recherche du delta_f_max associé aux swap de taches. Une fois trouvée, on réalise le swap.
        On retourne True ou False selon si la valeur actuelle du pb est un optimum local."""
    delta_f_max = 0
    best_swap = (0,0)
    # parcours du voisinage
    for t1 in range(pb.t):
        for t2 in range(t1):
            real, delta_f = cout_swap_taches(pb, t1,t2)
            # maj du delta_max et on garde le swap en mémoire.
            if real and delta_f >delta_f_max:
                delta_f_max = delta_f
                best_swap = (t1,t2)
    
    if delta_f_max!=0:
        # on a trouvé un meilleur voisin et on l'échange
        swap_taches(pb, delta_f_max, best_swap[0], best_swap[1])
        return False
    else:
        # c'est un optimum local
        return True
    
def descente_un_pas_swap(pb):
    """recherche du delta_f_min associé aux swap. Une fois trouvée, on réalise le swap.
        On retourne True ou False selon si la valeur actuelle du pb est un optimum local."""
    delta_f_min = 0
    best_swap = (0,0)
    # parcours du voisinage
    for t1 in range(pb.t):
        for t2 in range(t1):
            real, delta_f = cout_swap_taches(pb, t1,t2)
            # maj du delta_min et on garde le swap en mémoire.
            if real and delta_f < delta_f_min:
                delta_f_min = delta_f
                best_swap = (t1,t2)
    
    if delta_f_min!=0:
        # on a trouvé un meilleur voisin et on l'échange
        swap_taches(pb, delta_f_min, best_swap[0], best_swap[1])
        return False
    else:
        # c'est un optimum local
        return True
    
def montee_reaffectation_un_pas(pb):
    """recherche du delta_f_max associé à la réaffectation de tâches.
        Une fois trouvée, on réalise la réaffectation.
        On retourne True ou False selon si la valeur actuelle du pb est un optimum local."""
    delta_f_max = 0
    best_reaffect = (-1,-1)
    # parcours du voisinage
    for t in range(pb.t):
        for j in range(pb.m):
            real, delta_f = cout_reaffectation_1tache(pb, j,t)
            # print("real: ", real, "\tdelta: ", delta_f, "\tdelta_f_max: ", delta_f_max, "\t reaffect: ", t,j)
            if real and delta_f > delta_f_max:
                delta_f_max = delta_f 
                best_reaffect = (j,t)
                # print("changé" )
           # print("--------------------------")
    # reaffecation si amélioration
    if delta_f_max != 0:
        reaffectation_1tache(pb, delta_f_max, best_reaffect[0],best_reaffect[1])
        return False
    else:
        # c'est un optimum local
        return True
    
def descente_reaffectation_un_pas(pb):
    """recherche du delta_f_max associé à la réaffectation de tâches.
        Une fois trouvée, on réalise la réaffectation.
        On retourne True ou False selon si la valeur actuelle du pb est un optimum local."""
    delta_f_min = 0
    best_reaffect = (-1,-1)
    for t in range(pb.t):
        for j in range(pb.m):
            real, delta_f = cout_reaffectation_1tache(pb, j,t)
            if real and delta_f < delta_f_min:
                delta_f_min = delta_f
                best_reaffect = (j,t)
    if delta_f_min != 0:
        reaffectation_1tache(pb, delta_f_min, best_reaffect[0],best_reaffect[1])
        return False
    else:
        return True
    
# Fonctions pour appeler la bonne selon le critere choisi
 
def un_pas_swap(pb, critere = 'max'):
    if critere == 'max':
        return montee_un_pas_swap(pb)
    else:
        return descente_un_pas_swap(pb)
    
def un_pas_reaffectation(pb, critere = 'max'):
    if critere == 'max':
        return montee_reaffectation_un_pas(pb)
    else:
        return descente_reaffectation_un_pas(pb)
    
# *****************************************************************************************************************
# Fonctions de recherche locale.
# Limite de temps ou limite d'itérations
# *****************************************************************************************************************


def montee_iterMax(pb, fn_initialisation, fn_un_pas, critere = 'max', iterMax = 100, init = True):
    """Algorithme de montee en nombre max d'itérations.
        pb: une instance du problème, obj de la classe Pb. Cet objet conserve la valeur, la solution et les autres données du pb.
        fn_initialisation: fonction d'initialisation (trouver une première solution réalisable)
        fn_un_pas: fonction pour un pas de recherche locale
        critere: si on veut max ou min
        itermax: nb limite d'itérations
        init: bool si on veut initialiser ou partir de la solution actuelle du pb"""
    
    # initialisation des différentes valeurs
    if init:
        fn_initialisation(pb, critere)

    val_initiale = pb.eval()
    pb.capacites_residuelles()
    if not init_sol.est_complete(pb.x):
        # print("solution initiale non réalisable: toutes les tâches ne sont pas affectées.")
        pb.f = -1
        return None
    # iteration de la fonction de montee/descente
    for i in range(iterMax):
        opt_local = fn_un_pas(pb, critere)
        if opt_local:
            return pb.f
    
    # print("optimum local pas trouvé.")
    return pb.f


def montee(pb, fn_initialisation, fn_un_pas, init, critere = 'max', t_max = 300):
    """Algorithme de montee en nombre max d'itérations.
        pb: une instance du problème, obj de la classe Pb. Cet objet conserve la valeur, la solution et les autres données du pb.
        fn_initialisation: fonction d'initialisation (trouver une première solution réalisable)
        fn_un_pas: fonction pour un pas de recherche locale
        init: bool si on veut initialiser ou partir de la solution actuelle du pb
        critere: si on veut max ou min
        t_max: temps limite de l'exécution"""
    
    # print("initialisation..")
    if init:
        fn_initialisation(pb, critere)

    val_initiale = pb.eval()
    pb.capacites_residuelles()
    if not init_sol.est_complete(pb.x):
        print("solution initiale non réalisable: toutes les tâches ne sont pas affectées.")
        pb.f = -1
        return None
    s = time.time()
    t=s
    # si on dépasse le temps on s'arrête
    while t-s <= t_max:
        opt_local = fn_un_pas(pb, critere)
        if opt_local:
            return pb.f, val_initiale, pb.x, iter
        t = time.time()

    return pb.f, val_initiale, pb.x, iter

def montee_timeMax(pb, fn_initialisation, fn_un_pas, timeMax = 300, critere = 'max', init = True):
    """Algorithme de montee en nombre max d'itérations.
        pb: une instance du problème, obj de la classe Pb. Cet objet conserve la valeur, la solution et les autres données du pb.
        fn_initialisation: fonction d'initialisation (trouver une première solution réalisable)
        fn_un_pas: fonction pour un pas de recherche locale
        timeMax: temps limite d'exécution
        init: bool si on veut initialiser ou partir de la solution actuelle du pb
        critere: si on veut max ou min"""

    start = time.time()

    montee(pb, fn_initialisation, fn_un_pas, init, critere, t_max=timeMax)

    end = time.time()
    return pb.f, end-start

def montee_depMult_timeMax(pb, fn_initialisation, fn_un_pas, timeMax = 300, critere = 'max', init = True, nb_depart = 5):
    """Algorithme de montee en nombre max d'itérations.
        pb: une instance du problème, obj de la classe Pb. Cet objet conserve la valeur, la solution et les autres données du pb.
        fn_initialisation: fonction d'initialisation (trouver une première solution réalisable)
        fn_un_pas: fonction pour un pas de recherche locale
        timeMax: temps limite d'exécution
        init: bool si on veut initialiser ou partir de la solution actuelle du pb
        critere: si on veut max ou min
        nb_depart: le nombre de lancement de la recherche locale
        
        Pour être utile la fonction d'initialisation doit à chaque fois donner des solutions différentes."""

    start = time.time()
    valeurs = []
    solutions = []
    # on exécute la fonctions pour chaque départ
    for _ in range(nb_depart):
        real = fn_initialisation(pb, critere)
        if real:
            montee(pb, fn_initialisation, fn_un_pas, init, critere, timeMax/nb_depart)
            valeurs.append(pb.f)
            solutions.append(pb.x)
    
    # on sélectionne la meilleure solution
    valeurs = np.array(valeurs)
    if critere == 'max':
        best_val = np.max(valeurs)
        index_best = np.argmax(valeurs)
    else:
        best_val = np.min(valeurs)
        index_best = np.argmin(valeurs)
    
    best_sol = solutions[index_best]
    real = pb.realisabilite(best_sol)==0
    end = time.time()
    return best_val, best_sol, end-start



