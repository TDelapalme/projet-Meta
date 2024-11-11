import init_sol
import random
import recherche_taboue as rt
import voisinage as v
import copy
from concurrent.futures import ProcessPoolExecutor


def croisement(parent1,parent2):

    t = len(parent1)
    masque = [random.randint(0, 1) for _ in range(t)]
    enfant1, enfant2 = [-1] * t, [-1] * t
 
    #print('Avant croisement : ', init_sol.est_complete(parent1),init_sol.est_complete(parent2))   
    for i in range(t):
        if masque[i]==0:
            enfant1[i] = parent1[i]
            enfant2[i] = parent2[i]
        else:
            enfant1[i] = parent2[i]
            enfant2[i] = parent1[i]
    #print('Après croisement : ', init_sol.est_complete(enfant1),init_sol.est_complete(enfant2))
    return(enfant1,enfant2)

def mutation(sol, Pb, alpha):
    t = len(sol)
    nb_agents = Pb.m
    sol_copy = copy.deepcopy(sol)  
    count = 0
    for i in range(t):
        if random.random() < alpha:
            a = random.randint(0, nb_agents - 1)  # Ensure valid agent index
            sol_copy[i] = a  

            if Pb.realisabilite(sol_copy) == 0:  
                sol[i] = a  # Commit mutation if feasible
                count+=1
            else:
                sol_copy[i] = sol[i]  
    #print('nb mutations', count)
    return sol

def parent_selection(sols_fam, Pb, critere='max'): # Tournament
    N = len(sols_fam)
    sample_size = min(N//4,10)
    candidates = random.sample(sols_fam, sample_size)

    mid = sample_size//2
    candidates1, candidates2 = candidates[:mid], candidates[mid:]

    if critere == 'max':
        return max(candidates1, key=lambda x: Pb.evaluate(x)),max(candidates2, key=lambda x: Pb.evaluate(x))
    if critere == 'min':
        return min(candidates1, key=lambda x: Pb.evaluate(x)),min(candidates2, key=lambda x: Pb.evaluate(x))


def descente_pop_old(pop, Pb, max_tot_time, max_amelio_time, critere='max'):
    """Amélioration d'une population par recherche taboue

    Returns:
        pop: population améliorée
    """
    # nouvelle pop améliorée
    new_pop = [[]] * len(pop)

    # param recherche tabou
    taille_liste = int(Pb.t/4)
    fn_init = init_sol.sol_gloutonne_2
    fn_rt = rt.recherche_taboue
    critere_tabou = rt.tabou_liste_tache_reaffectation
    initialisation = False
    aspiration = True
    timeMax = max_tot_time
    timeMaxAmelio = max_amelio_time

    if critere == 'max':
        fn_un_pas = rt.montee_un_pas_tabou_reaffect_nvl_agent
        fn_un_pas_ls = v.un_pas_reaffectation

    else :
        fn_un_pas = rt.descente_un_pas_tabou_reaffect_nvl_agent
        fn_un_pas_ls = v.un_pas_reaffectation
        
    for i in range(len(pop)):
        Pb.x = pop[i]
        _, best_x, _, _ = rt.a_recherche_taboue_timeMax(Pb, fn_rt, fn_init, fn_un_pas, fn_un_pas_ls,critere_tabou, taille_liste, init = initialisation,
                                                                 aspiration = aspiration, critere = critere, timeMax = timeMax,
                                                                 timeMaxAmelio=timeMaxAmelio)
        new_pop[i] = best_x
    return new_pop

def improve_solution(sol, Pb, fn_rt, fn_init, fn_un_pas, fn_un_pas_ls, critere_tabou, taille_liste, 
                     initialisation, aspiration, critere, timeMax, timeMaxAmelio):
    """Helper function to improve a single solution using tabu search."""
    # Set the solution in the problem instance
    Pb.x = sol
    
    # Perform tabu search on the solution
    _, best_x, _, _ = rt.a_recherche_taboue_int_timeMax(
        Pb, fn_rt, fn_init, fn_un_pas, fn_un_pas_ls,
        critere_tabou, taille_liste, init=initialisation,
        aspiration=aspiration, critere=critere, timeMax=timeMax,
        timeMaxAmelio=timeMaxAmelio
    )
    return best_x

def descente_pop(pop, Pb, max_tot_time, max_amelio_time, critere='max'):
    # Parameters for tabu search
    taille_liste = int(Pb.t / 4)
    fn_init = init_sol.sol_gloutonne_2
    fn_rt = rt.recherche_taboue_int_div_2
    fn_un_pas_ls = v.un_pas_reaffectation
    critere_tabou = rt.tabou_liste_tache_reaffectation
    initialisation = False
    aspiration = True
    timeMax = max_tot_time
    timeMaxAmelio = max_amelio_time

    # Select appropriate functions based on the criterion
    if critere == 'max':
        fn_un_pas = rt.montee_un_pas_tabou_reaffect_nvl_agent
    else :
        fn_un_pas = rt.descente_un_pas_tabou_reaffect_nvl_agent
    
    # Use ProcessPoolExecutor for parallelization
    with ProcessPoolExecutor() as executor:
        futures = [
            executor.submit(improve_solution, sol, Pb, fn_rt, fn_init, fn_un_pas, fn_un_pas_ls, 
                            critere_tabou, taille_liste, initialisation, aspiration, critere, timeMax, timeMaxAmelio)
            for sol in pop
        ]

        # Collect the results as they complete
        new_pop = [future.result() for future in futures]

    return new_pop

def new_pop(sols_fam, Pb, alpha_mutation=0.1, critere='max'):
    
    N = len(sols_fam)
    children = [[-1 for _ in range(Pb.t)] for _ in range(N)]

    for i in range(N//2):
        p1,p2 = parent_selection(sols_fam, Pb,critere)
        child1, child2 = croisement(p1,p2)
        mutation(child1,Pb,alpha_mutation),mutation(child2,Pb,alpha_mutation)
        children[i*2] = child1
        children[i*2+1] = child2
    sorted_parents = sorted(sols_fam, key=lambda x : Pb.evaluate(x), reverse=(critere=='max'))
    sorted_children = sorted(children, key=lambda x : Pb.evaluate(x), reverse=(critere=='max'))

    # On ne garde que des solutions réalisables parmis les enfants, et on prend les N//2 meilleurs si possible
    real_children = []
    i = 0
    for child in sorted_children:
        if Pb.realisabilite(child) == 0 and i<(2*N)//3 and init_sol.est_complete(child):
            real_children.append(child)
            i+=1

    pop = sorted_parents[:N-len(real_children)] + real_children

    return pop

def best_element(pop, Pb, critere):
    sol_opt = None
    opt = None
    bol = True
    for sol in pop:
        #if not init_sol.est_complete(sol):
        #    print('sol non complète')
        #    bol = False
        if opt == None:
            if Pb.realisabilite(sol)==0:
                opt=Pb.evaluate(sol)
                sol_opt = sol
        else:
            if Pb.evaluate(sol)>opt and critere=='max' and Pb.realisabilite(sol)==0:
                opt=Pb.evaluate(sol)
                sol_opt = sol
            if Pb.evaluate(sol)<opt and critere=='min' and Pb.realisabilite(sol)==0:
                opt=Pb.evaluate(sol)
                sol_opt = sol
    #if bol:
    #    print('Toutes les solutions sont complètes')
    return sol_opt,opt
        
def count_real(pop,Pb):
    c=0
    for sol in pop:
        if Pb.realisabilite(sol)==0:
            c+=1
    return c

def evolution(Pb, N_init, N_gen_max, max_tot_time, max_amelio_time, alpha_mutation=0.1, critere='max', verbose=False):
    """
    Fonction principale pour l'évolution d'une population, à partir d'un problème donné, la foonction génrère 
    une première famille de solution admissible puis l'améliore avec une recherche taboue.
    A chaque nouvelle génération la population évolue (croisement + mutation) puis est amélioré par 
    recherche taboue sur chaque individu.
    Renvoie le meilleur individu et son évaluation pour chaque génération.
    """
    
    Bests = []  # Liste pour stocker les meilleures solutions à chaque génération
    
    # Génération de la population initiale à partir des solutions gloutonnes
    pop_init = init_sol.fam_sols(Pb, critere, N_init) 

    if verbose:
        for sol in pop_init:
            print(sol)
    
    # Filtrage des éléments None dans la population initiale
    pop_init = [sol for sol in pop_init if sol is not None]

    # Si la population est vide (aucune solution gloutonne valide), on arrête et retourne None
    if not pop_init:
        print("Pas de solution gloutonne trouvée dans le temps imparti")
        return None
    
    # Si la population initiale est trop petite (pas assez grande pour une évolution interessante), on retourne la meilleure
    if len(pop_init)<10:
        print("Pas assez de solutions gloutonnes trouvée dans le temps imparti")
        Best = best_element(pop_init, Pb, critere)
        Bests.append(Best)
        pop = descente_pop(pop_init, Pb, max_tot_time, max_amelio_time, critere)
        # Trouver la meilleure solution après la descente
        Best = best_element(pop, Pb, critere)
        Bests.append(Best)
        return Bests
    
    # Trouver la meilleure solution dans la population initiale
    Best = best_element(pop_init, Pb, critere)
    Bests.append(Best)
    
    if verbose:
        print('Meilleure solution gloutonne :', Best[1])

    # Amélioration de la population initiale avec recherche taboue
    pop = descente_pop(pop_init, Pb, max_tot_time, max_amelio_time, critere)
    
    # Trouver la meilleure solution après la descente
    Best = best_element(pop, Pb, critere)
    Bests.append(Best)
    
    if verbose:
        print('Meilleure solution après la première descente :', Best[1])

    max_stagnation = 5  # Nombre maximal de générations sans amélioration avant d'arrêter
    i_stagnation = 0  # Compteur de stagnation
    i = 0  # Compteur de générations
    
    while i < N_gen_max and i_stagnation < max_stagnation:
        if verbose:
            print(f'Gen {i} :')
            
        # Création des enfants (nouvelles solutions) par mutation ou croisement
        children = new_pop(pop, Pb, alpha_mutation, critere)

        for x in children:
            if not init_sol.est_complete(x):
                print(x)
        # Application de la descente sur la nouvelle population
        pop = descente_pop(children, Pb, max_tot_time, max_amelio_time, critere)
        
        # Trouver la meilleure solution parmi les enfants
        best_child = best_element(pop, Pb, critere)

        # Vérification si la solution enfant est meilleure que la meilleure solution trouvée
        if best_child[1] is not None:
            if (critere == 'max' and best_child[1] > Best[1]) or (critere == 'min' and best_child[1] < Best[1]):
                Best = copy.deepcopy(best_child)  # Mise à jour de la meilleure solution
                i_stagnation = 0  # Réinitialisation du compteur de stagnation
            else:
                i_stagnation += 1  # Incrémentation du compteur de stagnation
        else:
            i_stagnation += 1  # Incrémentation si la solution est None
        
        Bests.append(best_child)  # Ajout de la meilleure solution de cette génération à la liste des meilleures solutions
        
        if verbose:
            # Affichage de la meilleure solution de la génération actuelle
            print(f'Meilleure sol de la génération actuelle : {best_child[1]}')
        
        i += 1  # Passage à la génération suivante

    if verbose:
        if i_stagnation == max_stagnation:
            print('Stagnation de la meilleure solution.') 
        else:
            print('Maximum de générations atteint')

    return Bests  # Retourner les meilleures solutions trouvées à chaque génération



"""
Pb1 =  init_sol.Pb("instances/gap1.txt",0)
sols_fam = init_sol.fam_sols(Pb1)
"""