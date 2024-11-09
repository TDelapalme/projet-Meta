import init_sol
import random
import recherche_taboue as rt
import voisinage as v

def croisement(parent1,parent2):

    t = len(parent1)
    masque = [random.randint(0, 1) for _ in range(t)]
    enfant1, enfant2 = [-1] * t, [-1] * t

    for i in range(t):
        if masque[i]==0:
            enfant1[i] = parent1[i]
            enfant2[i] = parent2[i]
        else:
            enfant1[i] = parent2[i]
            enfant2[i] = parent1[i]

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
    fn_un_pas = rt.montee_un_pas_tabou_swap
    fn_rt = rt.recherche_taboue_int_div_2
    fn_un_pas_ls = v.un_pas_swap
    critere_tabou = rt.tabou_liste_1_swap
    initialisation = False
    critere = 'max'
    aspiration = True
    timeMax = 2
    timeMaxAmelio = 0.1


    for i in range(len(pop)):
        Pb.x = pop[i]
        #print(f'obj sol initiale : {Pb.eval()}')
        best_f, best_x, _, _ = rt.recherche_taboue_int_timeMax(Pb, fn_rt, fn_init, fn_un_pas, fn_un_pas_ls, critere_tabou, taille_liste, init = initialisation,
                                                                aspiration = aspiration, critere = critere,
                                                                timeMax = timeMax, timeMaxAmelio=timeMaxAmelio)
        new_pop[i] = best_x
        #print(f'obj sol finale : {best_f}')

    return new_pop

def new_pop(sols_fam, Pb, critere='max'):
    
    N = len(sols_fam)
    children = [[-1]*Pb.t]*N
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
    id_opt = 0
    opt = Pb.evaluate(pop[id_opt])
    for id in range(1,len(pop)):
        if Pb.evaluate(pop[id])>opt and critere=='max':
            opt=Pb.evaluate(pop[id])
            id_opt = id
        if Pb.evaluate(pop[id])<opt and critere=='min':
            opt=Pb.evaluate(pop[id])
            id_opt = id
    return id_opt,opt
        


def evolution(Pb,critere= 'max'):

    pop = descente_pop(init_sol.fam_sols(Pb,critere),Pb)
    best = best_element(pop,Pb,critere)
    N = 10 # nb de générations

    for i in range(N):
        children = new_pop(pop,Pb,critere)
        children_ameliores = descente_pop(children,Pb,critere)
        best_child = best_element(children_ameliores,Pb,critere)
        print(best_child[1])
        if best_child[1]>best[1]:
            best = best_child
    
    return best



"""
Pb1 =  init_sol.Pb("instances/gap1.txt",0)
sols_fam = init_sol.fam_sols(Pb1)
"""