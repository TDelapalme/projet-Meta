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

def mutation(sol,Pb,alpha):
    t = len(sol)
    nb_agents = Pb.m
    sol_copy = copy.deepcopy(sol)
    for i in range(t):
        if random.random()<alpha:
            a = random.randint(0,nb_agents)
            sol_copy[i] = a
            if Pb.realisabilite(sol_copy)==0:
                sol[i] = a
            else:
                sol_copy = copy.deepcopy(sol)
    return(sol)

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
    _, best_x, _, _ = rt.a_recherche_taboue_timeMax(
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
    fn_rt = rt.recherche_taboue
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

def new_pop(sols_fam, Pb, critere='max'):
    
    N = len(sols_fam)
    children = [[-1 for _ in range(Pb.t)] for _ in range(N)]

    for i in range(N//2):
        p1,p2 = parent_selection(sols_fam, Pb,critere)
        child1, child2 = croisement(p1,p2)
        child1, child2 = mutation(child1,Pb,0.1),mutation(child2,Pb,0.1)
        children[i*2] = child1
        children[i*2+1] = child2
    sorted_parents = sorted(sols_fam, key=lambda x : Pb.evaluate(x), reverse=(critere=='max'))
    sorted_children = sorted(children, key=lambda x : Pb.evaluate(x), reverse=(critere=='max'))

    # On ne garde que des solutions réalisables parmis les enfants, et on prend les N//2 meilleurs si possible
    real_children = []
    i = 0
    for child in sorted_children:
        if Pb.realisabilite(child) == 0 and i<(2*N)//3:
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

def evolution(Pb, N_init, N_gen_max, max_tot_time, max_amelio_time, critere= 'max'):

    pop_init = init_sol.fam_sols(Pb,critere,N_init)
    Best = best_element(pop_init,Pb,critere)
    print('Meileure solution de départ : ',Best[1])

    pop = descente_pop(pop_init,Pb,max_tot_time, max_amelio_time,critere)
    print('Meileure solution après la première descente : ',Best[1])
    max_stagnation = 3
    i_stagnation = 0
    i = 0
    
    while i<N_gen_max and i_stagnation<max_stagnation:
        print(f'Gen {i} :')
        children = new_pop(pop,Pb,critere)
        #print(f"Nb d'enfants réalisables avant descente : {count_real(children,Pb)}")
        pop = descente_pop(children,Pb,max_tot_time, max_amelio_time,critere)
        #print(f"Nb d'enfants réalisables apres descente : {count_real(pop,Pb)}")
        best_child = best_element(pop,Pb,critere)
        if best_child[1] :
            if critere=='max': 
                if best_child[1]>Best[1] :
                    Best = copy.deepcopy(best_child)
                    i_stagnation=0
                else:
                    i_stagnation+=1
            else:
                if best_child[1]<Best[1] :
                    Best = copy.deepcopy(best_child)
                    i_stagnation=0
                else:
                    i_stagnation+=1
        else:
            i_stagnation+=1

        print(f'Meilleure sol de la generation actuelle : {best_child[1]}')
        i+=1

    if i_stagnation == max_stagnation:
        print('Stagnation de la meilleure solution.')
    else:
        print('Maximun de générations atteint')

    print("Meilleure solution sur l'evolution : ",Best[1])

    return Best



"""
Pb1 =  init_sol.Pb("instances/gap1.txt",0)
sols_fam = init_sol.fam_sols(Pb1)
"""