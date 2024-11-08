import init_sol
import voisinage as v
import numpy as np
import queue
import time
from threading import Thread

# ******************************************************************************************************************************
# Classe de file pour la liste taboue efficace
# On remplace le premier entré par le dernier entré en temps constant de la taille max de la file.

class ListeTaboue:
    def __init__(self, taille_max):
        self.taille_max = taille_max
        self.liste = -np.ones((taille_max, 2))
        self.indice_fin = 0 # l'indice de la fin de la file
        pass

    def ajouter(self, element):
        # on remplace le dernier element de la file par le nouveau
        self.liste[self.indice_fin] = element
        # on change la fin
        self.indice_fin += 1
        # si la fin de la file est en bout de tableau, on la ramène au début
        if self.indice_fin == self.taille_max:
            self.indice_fin = 0
            
# *******************************************************************************************************************************
# Fonctions pour une étape de recherche taboue avec réaffectation 

# --------------------------------------------------------------------
# Critère d'appartenance à liste taboue.
# Pour les fonctions qui suivent l' element désigne le couple (agent, tache) 

def tabou_liste(liste, element):
    # liste tabou des derniers echanges inverses.
    return element in liste.liste

def tabou_liste_tache_reaffectation(liste, element):
    # on ne reaffecte pas une tâche qui a récemment été affecté
    j,t = element
    return t in liste.liste[:,1]

def tabou_liste_agent_reaffectation(liste, element):
    # on affecte pas de tache a un agent de la liste
    j,t = element
    return j in liste.liste[:,0]

def tabou_liste_couple_swap(liste,element):
    # on ne fait pas un swap de la liste
    t1,t2 = element
    return ((t1,t2) in liste.liste) or ((t2,t1) in liste.liste)

def tabou_liste_1_swap(liste, element):
    # on ne reaffecte pas une tâche qui a récemment été échangée
    t1,t2 = element
    return (t1 in liste.liste) or (t2 in liste.liste)

def tabou_liste_2_swap(liste, element):
    # on ne reaffecte pas deux tâches qui ont récemment été échangées
    t1,t2 = element
    return (t1 in liste.liste) and (t2 in liste.liste)

#----------------------------------------------------------------------
# Fonctions de montée d'un pas pour la réaffectation


def montee_un_pas_tabou_reaffect_ancien_agent(pb, best_f, critere_tabou, liste_taboue, aspiration = True):
    """ une étape de recherche taboue. On retourne True si on a amélioré la meilleur valeur best_f rencontrée jusqu'à présent
        et False sinon.
        La fonction prend le meilleur voisin qui n'est pas dans la liste taboue, effectue la réaffection et l'ajoute dans la liste.
        Les couples de la liste taboue sont les affectations qui ont été rompues..
        La variable aspiration indique s'il y a le critère d'aspiration."""
    
    delta_f_max = -np.max(pb.c)
    best_reaffect = (-1,-1)
    for t in range(pb.t):
        for j in range(pb.m):
            real, delta_f = v.cout_reaffectation_1tache(pb, j,t)
            if real and delta_f > delta_f_max:
                if aspiration and pb.f + delta_f > best_f:
                    delta_f_max = delta_f
                    best_reaffect = (j,t)
                elif not critere_tabou(liste_taboue, (j,t)):
                    delta_f_max = delta_f
                    best_reaffect = (j,t)

    ancien_agent = v.reaffectation_1tache(pb, delta_f_max, best_reaffect[0],best_reaffect[1])
    liste_taboue.ajouter(ancien_agent, best_reaffect[1])
    if pb.f > best_f:
        return True
    return False

def montee_un_pas_tabou_reaffect_nvl_agent(pb, best_f, critere_tabou, liste_taboue, aspiration = True):
    """ une étape de recherche taboue. On retourne True si on a amélioré la meilleur valeur best_f rencontrée jusqu'à présent
        et False sinon.
        La fonction prend le meilleur voisin qui n'est pas dans la liste taboue, effectue la réaffection et l'ajoute dans la liste.
        Les couples de la liste taboue sont les nouvelles affectations qui ont été faites.
        La variable aspiration indique s'il y a le critère d'aspiration."""
    
    delta_f_max = -np.max(pb.c)
    best_reaffect = (-1,-1)
    for t in range(pb.t):
        for j in range(pb.m):
            real, delta_f = v.cout_reaffectation_1tache(pb, j,t)
            if real and delta_f > delta_f_max:
                if aspiration and pb.f + delta_f > best_f:
                    delta_f_max = delta_f
                    best_reaffect = (j,t)
                elif critere_tabou(liste_taboue, (j,t)):
                    delta_f_max = delta_f
                    best_reaffect = (j,t)

    ancien_agent = v.reaffectation_1tache(pb, delta_f_max, best_reaffect[0],best_reaffect[1])
    liste_taboue.ajouter(best_reaffect[1])
    if pb.f > best_f:
        return True
    return False

#----------------------------------------------------------------------
# Fonctions de montée d'un pas pour le swap

def montee_un_pas_tabou_swap(pb, best_f, critere_tabou, liste_taboue, aspiration = True):
    """ une étape de recherche taboue. On retourne True si on a amélioré la meilleur valeur best_f rencontrée jusqu'à présent
        et False sinon.
        La fonction prend le meilleur voisin qui n'est pas dans la liste taboue, effectue la réaffection et l'ajoute dans la liste.
        Les couples de la liste taboue sont les affectations qui ont été rompues..
        La variable aspiration indique s'il y a le critère d'aspiration."""
    
    delta_f_max = -2*np.max(pb.c)
    best_reaffect = (-1,-1)
    for t1 in range(pb.t):
        for t2 in range(pb.t):
            real, delta_f = v.cout_swap_taches(pb, t1,t2)
            if real and delta_f > delta_f_max:
                if aspiration and pb.f + delta_f > best_f:
                    delta_f_max = delta_f
                    best_swap = (t1,t2)
                elif not critere_tabou(liste_taboue, (t1,t2)):
                    delta_f_max = delta_f
                    best_swap = (t1,t2)

    v.swap_taches(pb, delta_f_max, best_swap[0],best_swap[1])
    liste_taboue.ajouter(best_swap)
    if pb.f > best_f:
        return True
    return False
# *******************************************************************************************************************************
# Fonctions globales de recherche taboue
    
def recherche_taboue(pb, resultat, fn_init, fn_un_pas, critere_tabou, taille_liste,
                     init = True, aspiration = True, critere = 'max', timeMaxAmelio = 10):
    liste_taboue = ListeTaboue(taille_liste)
    if init:
        fn_init(pb, critere)

    best_f = pb.eval()
    val_initial = pb.f
    best_x = np.copy(pb.x)
    pb.capacites_residuelles()
    if not init_sol.est_complete(pb.x):
        print("solution initiale non réalisable: toutes les tâches ne sont pas affectées.")
        pb.f = -1
        resultat.put((-1, best_x, -1))
        return None
    derniere_amelioration = time.time()
    while not stopMontee:
        amelioree = fn_un_pas(pb, best_f, critere_tabou, liste_taboue, aspiration)
        tentative = time.time()
        if amelioree:
            best_f = pb.f
            best_x = np.copy(pb.x)
            derniere_amelioration = time.time()
        if tentative - derniere_amelioration >=timeMaxAmelio:
            print("pas d'amélioration en ", timeMaxAmelio,"s.")
            break
    
    resultat.put((best_f, best_x, val_initial))
    return None

def recherche_taboue_timeMax(pb, fn_init, fn_un_pas, critere_tabou, taille_liste,
                             init = True, aspiration = True, critere = 'max', timeMax = 300, timeMaxAmelio = 10):
    global stopMontee
    stopMontee = False
    resultat = queue.Queue()
    start = time.time()
    thread = Thread(target=recherche_taboue, args = [pb, resultat, fn_init, fn_un_pas, critere_tabou, taille_liste,
                                                     init, aspiration, critere, timeMaxAmelio])
    # Start the thread
    thread.start()

    # Join your thread with the execution time you want
    thread.join(timeMax)

    # Set off your flag switch to indicate that the thread should stop
    stopMontee = True
    end = time.time()
    best_f, best_x, val_initiale = resultat.get()
    return best_f, val_initiale, end-start, pb.realisabilite(best_x)==0
