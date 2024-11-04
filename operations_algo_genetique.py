import init_sol
import random

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

def parent_selection(sols_fam, Pb, tsize=10): # Tournament
    N = len(sols_fam)
    candidates = random.sample(sols_fam, tsize)

    mid = tsize // 2
    candidates1, candidates2 = candidates[:mid], candidates[mid:]

    return max(candidates1, key=lambda x: Pb.evaluate(x)),max(candidates2, key=lambda x: Pb.evaluate(x))

def corr_sol(sol):
    # renvoie une version réalisable d'une solution non réalisable
    return sol

def new_pop(sols_fam, Pb):
    
    N = len(sols_fam)
    children = [[-1]*Pb.t]*N
    for i in range(N//2):
        p1,p2 = parent_selection(sols_fam, Pb)
        child1, child2 = croisement(p1,p2)
        child1, child2 = corr_sol(child1), corr_sol(child2)
        children[i*2] = child1
        children[i*2+1] = child2
    sorted_parents = sorted(sols_fam, key=lambda x : Pb.evaluate(x), reverse=True)
    sorted_children = sorted(children, key=lambda x : Pb.evaluate(x), reverse=True)

    pop = sorted_parents[:10] + sorted_children[10:]

    return pop

"""
Pb1 =  init_sol.Pb("instances/gap1.txt",0)
sols_fam = init_sol.fam_sols(Pb1)
"""