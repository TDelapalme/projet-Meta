import init_sol
import random
import recherche_taboue as rt
import voisinage as v
import copy

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
    for i in range(t):
        if random.random()<alpha:
            a = random.randint(0,nb_agents)
            sol[i] = a
    return(sol)

def parent_selection(sols_fam, Pb, critere='max', tsize=10): # Tournament
    N = len(sols_fam)
    candidates = random.sample(sols_fam, tsize)

    mid = tsize // 2
    candidates1, candidates2 = candidates[:mid], candidates[mid:]

    if critere == 'max':
        return max(candidates1, key=lambda x: Pb.evaluate(x)),max(candidates2, key=lambda x: Pb.evaluate(x))
    if critere == 'min':
        return min(candidates1, key=lambda x: Pb.evaluate(x)),min(candidates2, key=lambda x: Pb.evaluate(x))

def corr_sol(sol):
    # renvoie une version réalisable d'une solution non réalisable

    return sol

def descente_pop(pop, Pb,critere='max'):

    # nouvelle pop améliorée
    new_pop = [[]] * len(pop)

    # param recherche tabou
    taille_liste = int(Pb.t/4)
    fn_init = init_sol.sol_gloutonne_2
    fn_rt = rt.recherche_taboue
    critere_tabou = rt.tabou_liste_tache_reaffectation
    initialisation = False
    aspiration = True
    timeMax = 2
    timeMaxAmelio = 0.1

    if critere == 'max':
        fn_un_pas = rt.montee_un_pas_tabou_reaffect_nvl_agent
        fn_un_pas_ls = v.un_pas_reaffectation

    else :
        fn_un_pas = rt.descente_un_pas_tabou_reaffect_nvl_agent
        fn_un_pas_ls = v.un_pas_reaffectation
        


    for i in range(len(pop)):
        Pb.x = pop[i]
        #print(f'obj sol initiale : {Pb.eval()}')
        #print(Pb.x)
        #print('Avant descente : ',init_sol.est_complete(Pb.x))

        best_f, best_x, _, _ = rt.recherche_taboue_timeMax(Pb, fn_rt, fn_init, fn_un_pas, fn_un_pas_ls,critere_tabou, taille_liste, init = initialisation,
                                                                 aspiration = aspiration, critere = critere, timeMax = timeMax,
                                                                 timeMaxAmelio=timeMaxAmelio)
        new_pop[i] = best_x
        #print('Apres descente : ',init_sol.est_complete(best_x))
        #print(f'obj sol finale : {best_f}')

    return new_pop

def new_pop(sols_fam, Pb, critere='max'):
    
    N = len(sols_fam)
    children = [[-1 for _ in range(Pb.t)] for _ in range(N)]

    for i in range(N//2):
        p1,p2 = parent_selection(sols_fam, Pb,critere)
        child1, child2 = croisement(p1,p2)
        child1, child2 = corr_sol(child1), corr_sol(child2)
        children[i*2] = child1
        children[i*2+1] = child2
    sorted_parents = sorted(sols_fam, key=lambda x : Pb.evaluate(x), reverse=(critere=='max'))
    sorted_children = sorted(children, key=lambda x : Pb.evaluate(x), reverse=(critere=='max'))

    pop = sorted_parents[:10] + sorted_children[10:]
    
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
        


def evolution(Pb, N_init, N_gen_max, critere= 'max'):

    #print('init...')
    pop_init = init_sol.fam_sols(Pb,critere,N_init)
    #print('Selection du meilleur individu...')
    Best = best_element(pop_init,Pb,critere)
    #print('Meileure solution de départ : ',Best[0],Best[1])

    #print('init 1', init_sol.est_complete(best[0]),best[0])
    #print('1ere Descente...')
    pop = descente_pop(pop_init,Pb)
    max_stagnation = 3
    i_stagnation = 0
    i = 0
    
    #print('init 2', init_sol.est_complete(best[0]),best[0])
    while i<N_gen_max and i_stagnation<max_stagnation:
        #print(f'Gen {i} :')
        #print(i,'Nouvelle pop ...')
        #print(Best)
        children = new_pop(pop,Pb,critere)
        #print(Best)
        #print(i,'Descente nouvelle pop ...')
        pop = descente_pop(children,Pb,critere)
        #print(Best)
        #print(i,'Selection du meilleur individu...')
        best_child = best_element(pop,Pb,critere)
        #print(Best)
        #print(i,'Meileure solution nouvelle pop : ',best_child[0],best_child[1])
        #print('best child : ',best_child[0], best_child[1])
        #print(Best)
        if best_child[1] :
            #print(Best)
            if best_child[1]>Best[1]:
                #print(Best)
                Best = copy.deepcopy(best_child)
                #print(Best)
                #print(i,'New best')
                i_stagnation=0
                #print(Best)
                #print(f'while it {i}, new best',init_sol.est_complete(best[0]), best[0])
            else:
                i_stagnation+=1
                #print(i,'Stagnation : ', i_stagnation)
                #print(f'while it {i}, not new best',init_sol.est_complete(best[0]),best[0])
        else:
            i_stagnation+=1
            #print(i,'Stagnation : ', i_stagnation)

        #print('Best : ',Best[0])
        i+=1
    if i_stagnation == max_stagnation:
        print('Stagnation de la meilleure solution.')
    else:
        print('Maximun de générations atteint')

    #print('End 1',init_sol.est_complete(best[0]))
    print('Meilleure solution sur l evolution : ',Best[0],Best[1])
    #print('End 2',init_sol.est_complete(best[0]))
    return Best



"""
Pb1 =  init_sol.Pb("instances/gap1.txt",0)
sols_fam = init_sol.fam_sols(Pb1)
"""