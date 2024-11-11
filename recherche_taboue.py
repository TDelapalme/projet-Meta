import init_sol
import voisinage as v
import numpy as np
import queue
import time

# ce fichier implémente les algorithmes de recherche taboue
# Les différentes parties:
#     - la classe de la liste tabou_liste
#     - les fonctions de criteres tabous
#     - les fonctions d'une étape de recherche taboue
#         - montée/descente pour la réaffection
#         - montée/descente pour le swap
#     - les differentes fonctions de recherche tabou (basique, intensification, diversification)
#     - les fonctions à appeler (basique, intensification, depart multiples)

# ******************************************************************************************************************************
# Classe de file pour la liste taboue efficace
# On remplace le premier entré par le dernier entré en temps constant de la taille max de la file.
# ******************************************************************************************************************************

class ListeTaboue:
    def __init__(self, taille_max):
        self.taille_max = taille_max
        self.liste = -np.ones((taille_max, 2))
        self.indice_fin = 0 # l'indice de la fin de la file
        pass

    def ajouter(self, element):
        # on remplace le dernier element de la file par le nouveau
        self.liste[self.indice_fin][0] = element[0]
        self.liste[self.indice_fin][1] = element[1]
        # on change la fin
        self.indice_fin += 1
        # si la fin de la file est en bout de tableau, on la ramène au début
        if self.indice_fin == self.taille_max:
            self.indice_fin = 0
        pass

    def vider(self):
        self.liste = -np.ones((self.taille_max, 2))
        self.indice_fin = 0
        pass

    def reduire(self, taille_max):
        copie = np.copy(self.liste)
        self.liste = -np.ones((taille_max, 2))
        for i in range(1,taille_max+1):
            self.liste[-i][0] = copie[(self.indice_fin-i)%taille_max][0]
            self.liste[-i][1] = copie[(self.indice_fin-i)%taille_max][1]
        self.indice_fin = 0
        self.taille_max = taille_max
            
    def etendre(self, taille_max):
        copie = np.copy(self.liste)
        self.liste = -np.ones((taille_max, 2))
        for i in range(self.taille_max):
            self.liste[i][0] = copie[(i+self.indice_fin)%self.taille_max][0]
            self.liste[i][1] = copie[(i+self.indice_fin)%self.taille_max][1]
        self.indice_fin = self.taille_max
        self.taille_max = taille_max

# ******************************************************************************************************************************
# Fonctions de critere d'appartenance à la liste taboue
# ******************************************************************************************************************************

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

# ******************************************************************************************************************************
# Fonctions d'une étape pour la recherche taboue
# ******************************************************************************************************************************

#--Montée pour réaffectation ou swap---------------------------------------------------------------------------------------------

# Cette fonction ajoute le couple (agent, tache) qui a été rompue à la réaffectation

def montee_un_pas_tabou_reaffect_ancien_agent(pb, best_f, critere_tabou, liste_taboue, aspiration = True):
    """ une étape de recherche taboue. On retourne True si on a amélioré la meilleur valeur best_f rencontrée jusqu'à présent
        et False sinon.
        La fonction prend le meilleur voisin qui n'est pas dans la liste taboue, effectue la réaffection et l'ajoute dans la liste.
        Les couples de la liste taboue sont les affectations qui ont été rompues..
        La variable aspiration indique s'il y a le critère d'aspiration."""
    
    delta_f_max = -10000 # valeur en temps constant qui convient à toutes les instances. Sinon - somme des couts.
    best_reaffect = (-1,-1)
    # parcours du voisinage
    for t in range(pb.t):
        for j in range(pb.m):
            real, delta_f = v.cout_reaffectation_1tache(pb, j,t)
            if real and delta_f > delta_f_max:
                # si realisable et que c'est le meilleur voisin rencontré
                if aspiration and pb.f + delta_f > best_f and j!= pb.x[t]: #critere d'aspiration
                    delta_f_max = delta_f
                    best_reaffect = (j,t)
                elif not critere_tabou(liste_taboue, (j,t)):
                    delta_f_max = delta_f
                    best_reaffect = (j,t)
    # on reaffecte le meilleur voisin
    # si on n'a pas trouve de voisin realisable qui n'est pas taboue alors on met (-1,-1) dans la liste
    # et on s'échappera au bout d'un moment de l'impasse en revenant par là où on est arrivé.
    ancien_agent = v.reaffectation_1tache(pb, delta_f_max, best_reaffect[0],best_reaffect[1])
    liste_taboue.ajouter((ancien_agent, best_reaffect[1]))
    if pb.f > best_f:
        return True
    return False


# Cette fonction ajoute le couple (agent, tache) qui a été créé à la réaffectation

def montee_un_pas_tabou_reaffect_nvl_agent(pb, best_f, critere_tabou, liste_taboue, aspiration = True):
    """ une étape de recherche taboue. On retourne True si on a amélioré la meilleur valeur best_f rencontrée jusqu'à présent
        et False sinon.
        La fonction prend le meilleur voisin qui n'est pas dans la liste taboue, effectue la réaffection et l'ajoute dans la liste.
        Les couples de la liste taboue sont les nouvelles affectations qui ont été faites.
        La variable aspiration indique s'il y a le critère d'aspiration."""
    delta_f_max = -100000
    best_reaffect = (-1,-1)
    for t in range(pb.t):
        for j in range(pb.m):
            real, delta_f = v.cout_reaffectation_1tache(pb, j,t)
            if real and delta_f > delta_f_max and j!= pb.x[t]:
                if aspiration and pb.f + delta_f > best_f:
                    delta_f_max = delta_f
                    best_reaffect = (j,t)
                elif not critere_tabou(liste_taboue, (j,t)):
                    # print("critere taboue non")
                    delta_f_max = delta_f
                    best_reaffect = (j,t)
 
    ancien_agent = v.reaffectation_1tache(pb, delta_f_max, best_reaffect[0],best_reaffect[1])
    liste_taboue.ajouter(best_reaffect)
    # print(liste_taboue.liste)

    return pb.f > best_f



def montee_un_pas_tabou_swap(pb, best_f, critere_tabou, liste_taboue, aspiration = True):
    """ une étape de recherche taboue. On retourne True si on a amélioré la meilleur valeur best_f rencontrée jusqu'à présent
        et False sinon.
        La fonction prend le meilleur voisin qui n'est pas dans la liste taboue, effectue la réaffection et l'ajoute dans la liste.
        Les couples de la liste taboue sont les affectations qui ont été rompues..
        La variable aspiration indique s'il y a le critère d'aspiration."""
    
    delta_f_max = -10000
    mod = False
    best_swap = (-1,-1)
    for t1 in range(pb.t):
        for t2 in range(t1+1,pb.t):
            real, delta_f = v.cout_swap_taches(pb, t1,t2)
            if real and delta_f > delta_f_max and pb.x[t1]!=pb.x[t2]:

                if aspiration and pb.f + delta_f > best_f:
                    delta_f_max = delta_f
                    best_swap = (t1,t2)
                    mod = True
                elif not critere_tabou(liste_taboue, (t1,t2)):
                    delta_f_max = delta_f
                    best_swap = (t1,t2)
    # print(best_swap, delta_f_max, pb.x[best_swap[0]]==pb.x[best_swap[1]] )
    v.swap_taches(pb, delta_f_max, best_swap[0],best_swap[1])
    liste_taboue.ajouter(best_swap)
    return pb.f > best_f

    

#--Descente pour réaffectation ou swap---------------------------------------------------------------------------------------------


def descente_un_pas_tabou_reaffect_ancien_agent(pb, best_f, critere_tabou, liste_taboue, aspiration = True):
    """ une étape de recherche taboue. On retourne True si on a amélioré la meilleur valeur best_f rencontrée jusqu'à présent
        et False sinon.
        La fonction prend le meilleur voisin qui n'est pas dans la liste taboue, effectue la réaffection et l'ajoute dans la liste.
        Les couples de la liste taboue sont les affectations qui ont été rompues..
        La variable aspiration indique s'il y a le critère d'aspiration."""
    
    delta_f_min = np.max(pb.c)
    best_reaffect = (-1,-1)
    for t in range(pb.t):
        for j in range(pb.m):
            real, delta_f = v.cout_reaffectation_1tache(pb, j,t)
            if real and delta_f < delta_f_min and j!= pb.x[t]:
                if aspiration and pb.f + delta_f < best_f:
                    delta_f_min = delta_f
                    best_reaffect = (j,t)
                elif not critere_tabou(liste_taboue, (j,t)):
                    delta_f_min = delta_f
                    best_reaffect = (j,t)

    ancien_agent = v.reaffectation_1tache(pb, delta_f_min, best_reaffect[0],best_reaffect[1])
    liste_taboue.ajouter((ancien_agent, best_reaffect[1]))
    if pb.f < best_f:
        return True
    return False

def descente_un_pas_tabou_reaffect_nvl_agent(pb, best_f, critere_tabou, liste_taboue, aspiration = True):
    """ une étape de recherche taboue. On retourne True si on a amélioré la meilleur valeur best_f rencontrée jusqu'à présent
        et False sinon.
        La fonction prend le meilleur voisin qui n'est pas dans la liste taboue, effectue la réaffection et l'ajoute dans la liste.
        Les couples de la liste taboue sont les nouvelles affectations qui ont été faites.
        La variable aspiration indique s'il y a le critère d'aspiration."""
    
    delta_f_min = 100000
    best_reaffect = (-1,-1)
    for t in range(pb.t):
        for j in range(pb.m):
            real, delta_f = v.cout_reaffectation_1tache(pb, j,t)
            if real and delta_f < delta_f_min and j!= pb.x[t]:
                if aspiration and pb.f + delta_f < best_f:
                    delta_f_min = delta_f
                    best_reaffect = (j,t)
                elif not critere_tabou(liste_taboue, (j,t)):
                    delta_f_min = delta_f
                    best_reaffect = (j,t)

    ancien_agent = v.reaffectation_1tache(pb, delta_f_min, best_reaffect[0],best_reaffect[1])
    liste_taboue.ajouter(best_reaffect)
    return pb.f < best_f


def descente_un_pas_tabou_swap(pb, best_f, critere_tabou, liste_taboue, aspiration = True):
    """ une étape de recherche taboue. On retourne True si on a amélioré la meilleur valeur best_f rencontrée jusqu'à présent
        et False sinon.
        La fonction prend le meilleur voisin qui n'est pas dans la liste taboue, effectue la réaffection et l'ajoute dans la liste.
        Les couples de la liste taboue sont les affectations qui ont été rompues..
        La variable aspiration indique s'il y a le critère d'aspiration."""
    
    delta_f_min = 10000
    mod = False
    best_swap = (-1,-1)
    for t1 in range(pb.t):
        for t2 in range(t1+1,pb.t):
            real, delta_f = v.cout_swap_taches(pb, t1,t2)
            if real and delta_f < delta_f_min and pb.x[t1]!=pb.x[t2]:

                if aspiration and pb.f + delta_f < best_f:
                    delta_f_min = delta_f
                    best_swap = (t1,t2)
                    mod = True
                elif not critere_tabou(liste_taboue, (t1,t2)):
                    delta_f_min = delta_f
                    best_swap = (t1,t2)
                    mod = True
    # print(best_swap, delta_f_max, pb.x[best_swap[0]]==pb.x[best_swap[1]] )
    if mod:
        v.swap_taches(pb, delta_f_min, best_swap[0],best_swap[1])
        liste_taboue.ajouter(best_swap)
        return pb.f < best_f
    else:
        return False
    
# *******************************************************************************************************************************
# Fonctions de recherche taboue
# *******************************************************************************************************************************


def recherche_taboue(pb, resultat, fn_init, fn_un_pas, critere_tabou, taille_liste,
                     init = True, aspiration = True, critere = 'max',t_max = 300, timeMaxAmelio = 10):
    """recherche taboue initiale. On s'interrompt si la solution n'a pas été améliorée pendant timeMaxAmelio secondes.
        pb: objet de l'instance
        resultat: une file dans laquelle on met le résultat
        fn_init: la fonction d'initialisation
        fn_un_pas: la fonction à un pas de recherche taboue
        critere_tabou: le critere choisi
        taille_liste: taille de la liste taboue
        init: bool si initialisatio
        aspiration: bool critere d'aspiration
        critere: max ou min
        t_max: le temps total limite d'exécution
        timeMaxAmelio: le temps max sans amélioration avant interruption
        """
    # initialisation
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
        resultat.put((None, best_x, -1))
        return None
    
    derniere_amelioration = time.time()
    s = time.time()
    t=s
    # recherche taboue
    while t-s <= t_max:
        amelioree = fn_un_pas(pb, best_f, critere_tabou, liste_taboue, aspiration) #fnc de recherche taboue
        tentative = time.time()
        if amelioree:
            best_f = pb.f
            best_x = np.copy(pb.x)
            derniere_amelioration = time.time()
        if tentative - derniere_amelioration >=timeMaxAmelio: #interruption si timeMaXAmelio s sans amélioration
            #print("pas d'amélioration en ", timeMaxAmelio,"s.")
            break
        t=time.time()
    
    resultat.put((best_f, best_x, val_initial))
    return None

def improved(best_f,f,critere):
    if critere =='max':
        return f>best_f
    else:
        return f<best_f

def recherche_taboue_intensification(pb, resultat, fn_init, fn_un_pas, fn_un_pas_ls, critere_tabou, taille_liste,
                     init = True, aspiration = True, critere = 'max',t_max = 300, timeMaxAmelio = 10):
    """ recherche taboue initiale avec intensification.
    On realise une recherche locale simple pour chaque solution prometteuse (=proche de la meilleure rencontrée)
    Apres on repart de cette solution comme départ (avec une liste taboue vide)."""
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
        resultat.put((None, best_x, -1))
        return None
    derniere_amelioration = time.time()
    s = time.time()
    t = s
    while t-s <= t_max:
        amelioree = fn_un_pas(pb, best_f, critere_tabou, liste_taboue, aspiration)
        tentative = time.time()

        # intensification
        if amelioree or abs(best_f - pb.f)/best_f <=0.05: # solution prometteuse
            # on realise une recherche locale sur cette solution prometteuse.
            f, temps = v.montee_timeMax(pb, fn_init, fn_un_pas_ls, timeMax = 2, critere = critere, init = False)
            liste_taboue.vider()
        if improved(best_f, pb.f, critere):
            best_f = pb.f
            best_x = np.copy(pb.x)
            derniere_amelioration = time.time()
        if tentative - derniere_amelioration >=timeMaxAmelio:
            #print("pas d'amélioration en ", timeMaxAmelio,"s.")
            break
        t = time.time()
    
    resultat.put((best_f, best_x, val_initial))
    return None

def recherche_taboue_div(pb, resultat, fn_init, fn_un_pas, critere_tabou, taille_liste,
                     init = True, aspiration = True, critere = 'max',t_max = 300, timeMaxAmelio = 10):
    """Au bout de la moitié du temps limite sans amélioration, on augmente la taille de la liste taboue"""
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
        resultat.put((None, best_x, -1))
        return None
    derniere_amelioration = time.time()
    s = time.time()
    t=s
    augmentation_liste = False
    while t-s <= t_max:
        amelioree = fn_un_pas(pb, best_f, critere_tabou, liste_taboue, aspiration)
        tentative = time.time()
        if amelioree:
            best_f = pb.f
            best_x = np.copy(pb.x)
            liste_taboue.reduire(taille_liste)
            augmentation_liste = False
            derniere_amelioration = time.time()

        # diversification
        elif not augmentation_liste and tentative - derniere_amelioration >=timeMaxAmelio//2:
            liste_taboue.etendre(int(liste_taboue.taille_max*2))
            augmentation_liste = True
        if tentative - derniere_amelioration >= timeMaxAmelio:
            #print("pas d'amélioration en ", timeMaxAmelio,"s.")
            break
        t=time.time()
    
    resultat.put((best_f, best_x, val_initial))
    return None

def recherche_taboue_int_div_2(pb, resultat, fn_init, fn_un_pas, fn_un_pas_ls, critere_tabou, taille_liste,
                     init = True, aspiration = True, critere = 'max',t_max = 300, timeMaxAmelio = 10):
    # Recherche taboue avec intensification et diversification. On combine les deux précédentes

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
        resultat.put((None, best_x, -1))
        return None
    derniere_amelioration = time.time()
    augmentation_liste = False # pour n'augmenter qu'une seule fois la taille de la liste
    s = time.time()
    t=s
    while t-s <= t_max:
        amelioree = fn_un_pas(pb, best_f, critere_tabou, liste_taboue, aspiration)
        tentative = time.time()
        
        # intensification
        if amelioree or abs(best_f - pb.f)/best_f <=0.01: # solution prometteuse

            f = v.montee_timeMax(pb, fn_init, fn_un_pas_ls, critere = critere, init = False, timeMax=timeMaxAmelio/10)
            
        if improved(best_f, pb.f, critere):
            best_f = pb.f
            best_x = np.copy(pb.x)
            liste_taboue.reduire(taille_liste)
            augmentation_liste = False # remise a 0
            derniere_amelioration = time.time()

        # diversification
        elif not augmentation_liste and tentative - derniere_amelioration >=timeMaxAmelio//2:
            liste_taboue.etendre(int(liste_taboue.taille_max*2))
            augmentation_liste = True
        if tentative - derniere_amelioration >= timeMaxAmelio:
            #print("pas d'amélioration en ", timeMaxAmelio,"s.")
            break
        t=time.time()
    
    resultat.put((best_f, best_x, val_initial))
    return None

# ***************************************************************************************************************
# Fonctions a appeler
# ***************************************************************************************************************

# recherche taboue classique ou avec diversification avec limite de temps.
def a_recherche_taboue_timeMax(pb, fn_rt, fn_init, fn_un_pas, fn_un_pas_ls, critere_tabou, taille_liste,
                             init = True, aspiration = True, critere = 'max', timeMax = 300, timeMaxAmelio = 10):

    resultat = queue.Queue()
    start = time.time()

    fn_rt(pb, resultat, fn_init, fn_un_pas, critere_tabou, taille_liste,
          init, aspiration, critere,timeMax, timeMaxAmelio)
    
    end = time.time()
    best_f, best_x, val_initiale = resultat.get()
    return best_f, best_x, end-start, pb.realisabilite(best_x)==0


# recherche taboue avec fonction d'intensification = recherche locale. 
# Limite de temps pour le global et limite d'itération hardcodée pour la recherche locale
def a_recherche_taboue_int_timeMax(pb, fn_rt, fn_init, fn_un_pas, fn_un_pas_ls, critere_tabou, taille_liste,
                             init = True, aspiration = True, critere = 'max', timeMax = 300, timeMaxAmelio = 10):
    resultat = queue.Queue()
    start = time.time()

    fn_rt(pb, resultat, fn_init, fn_un_pas, fn_un_pas_ls, critere_tabou, taille_liste,
          init, aspiration, critere,timeMax, timeMaxAmelio)

    end = time.time()
    best_f, best_x, val_initiale = resultat.get()
    return best_f, best_x, end-start, pb.realisabilite(best_x)==0

# une des recherche taboue précédentes avec départ multiples. Limite de temps
# A utiliser avec une fonction d'initialisation aléatoire
def a_recherche_taboue_depart_mult(pb, fn_rt_gbl, fn_rt, fn_init, fn_un_pas, fn_un_pas_ls, critere_tabou, taille_liste,
                                 init = True, aspiration = True, critere = 'max', timeMax = 300, timeMaxAmelio = 12, nb_depart = 10):
    s = time.time()
    valeurs = []
    solutions = []
    for dep in range(nb_depart):
        best_f, best_x,_, real = fn_rt_gbl(pb, fn_rt, fn_init, fn_un_pas, fn_un_pas_ls, critere_tabou, taille_liste,
                                           init, aspiration, critere, timeMax = timeMax/nb_depart, timeMaxAmelio = timeMaxAmelio)
        if real:
            valeurs.append(best_f)
            solutions.append(best_x)

    # on choisit la meilleure solution
    valeurs = np.array(valeurs)
    if critere == 'max':
        best_val = np.max(valeurs)
        index_best = np.argmax(valeurs)
    else:
        best_val = np.min(valeurs)
        index_best = np.argmin(valeurs)
    
    best_sol = solutions[index_best]
    real = pb.realisabilite(best_sol)==0
    e = time.time()
    return best_val, best_sol, e-s, real