import numpy as np
import init_sol
from threading import Thread
import time
import queue

def reaffectation_1tache(pb, delta_f,j,t):
    # reaffectation de la tache t a l'agent j
    # nouvelle valeur de la fonction objectif
    pb.f = pb.f + delta_f
    # maj des capcitées résiduelles 
    pb.b_res[pb.x[t]]  = pb.b_res[pb.x[t]] + pb.r[pb.x[t],t]
    pb.b_res[j] = pb.b_res[j] + pb.r[j,t]
    # affectation
    pb.x[t] = j
    pass

def cout_reaffectation_1tache(pb, j,t):
    # calcul de réalisabilité et de la nouvelle valeur
    delta_f = - pb.c[pb.x[t],t] + pb.c[j,t]
    realisable =(pb.b_res[j] - pb.r[j,t] >= 0)
    return realisable, delta_f
    
def swap_taches(pb, delta_f, t1,t2):
    # nouvelle valeur de la fonction objectif
    pb.f = pb.f + delta_f
    # maj des capacités résiduelles
    pb.b_res[pb.x[t2]] = pb.b_res[pb.x[t2]] + pb.r[pb.x[t1],t2]
    pb.b_res[pb.x[t1]] = pb.b_res[pb.x[t1]] + pb.r[pb.x[t2],t1]
    # swap des taches
    i1 = pb.x[t1]
    pb.x[t1] = pb.x[t2]
    pb.x[t2] = i1
    pass

def cout_swap_taches(pb,t1,t2):
    delta_f = - pb.c[pb.x[t1],t1] - pb.c[pb.x[t2],t2] + pb.c[pb.x[t2],t1] + pb.c[pb.x[t1],t2]
    realisable =(pb.b_res[pb.x[t1]] - pb.r[pb.x[t1],t2] >= 0) and (pb.b_res[pb.x[t2]] - pb.r[pb.x[t2],t1] >= 0)
    return realisable, delta_f


def montee_un_pas_swap(pb):
    """recherche du delta_f_min associé aux swap. Une fois trouvée, on réalise le swap.
        On retourne True ou False selon si la valeur actuelle du pb est un optimum local."""
    delta_f_max = 0
    best_swap = (0,0)
    # parcours du voisinage
    for t1 in range(pb.t):
        for t2 in range(t1):
            real, delta_f = cout_swap_taches(pb, t1,t2)
            # maj du delta_min et on garde le swap en mémoire.
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
    
def montee_iterMax(pb, fn_initialisation, fn_montee_un_pas, iterMax = 100):
    print("initialisation..")
    fn_initialisation(pb)
    print(pb.x)
    val_initiale = pb.eval()
    if not init_sol.est_complete(pb.x):
        print("solution initiale non réalisable: toutes les tâches ne sont pas affectées.")
        return None
    for i in range(iterMax):
        opt_local = fn_montee_un_pas(pb)
        if opt_local:
            return pb.f, val_initiale, pb.x, i
    
    print("optimum local pas trouvé.")
    return pb.f, val_initiale, pb.x, i

def un_pas_swap(pb, critere = 'max'):
    if critere == 'max':
        return montee_un_pas_swap(pb)
    else:
        return descente_un_pas_swap(pb)

def montee(pb, fn_initialisation, fn_un_pas, critere = 'max'):
    # print("initialisation..")
    fn_initialisation(pb, critere)
    val_initiale = pb.eval()
    if not init_sol.est_complete(pb.x):
        print("solution initiale non réalisable: toutes les tâches ne sont pas affectées.")
        pb.f = -1
        return None
    iter = 0
    while not stopMontee:
        opt_local = fn_un_pas(pb, critere)
        if opt_local:
            # print("optimum local trouvé")
            return pb.f, val_initiale, pb.x, iter
        iter +=1
    
    # print("optimum local pas trouvé.")
    return pb.f, val_initiale, pb.x, iter

def montee_timeMax(pb, fn_initialisation, fn_un_pas, timeMax = 300, critere = 'max'):
    global stopMontee
    stopMontee = False
    start = time.time()
    thread = Thread(target=montee, args = [pb, fn_initialisation, fn_un_pas, critere])
    # Start the thread
    thread.start()

    # Join your thread with the execution time you want
    thread.join(timeMax)

    # Set off your flag switch to indicate that the thread should stop
    stopMontee = True
    end = time.time()
    return pb.f, end-start



