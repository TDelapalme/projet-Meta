import readfiles
import random
import numpy as np

# Param
alpha = 0.5

class Pb:

    def __init__(self, file, id) -> None:
        self.file = file
        self.id = id
        self.r, self.c, self.b, self.m, self.t = readfiles.readfile(file,1)
        #self.X = [-1]*self.t

    def evaluate(self,X):
        f = 0
        for tache in range(len(X)):
            a = X[tache]
            f += self.c[a,tache]
        return f
    
    def realisabilite_agent(self, agent, X):
        # Vérifie si un agent peut effectuer les tâches qui lui sont assignées
        capacite_restante = self.b[agent]
        for tache in range(self.t):
            if X[tache] == agent:
                capacite_restante -= self.r[agent][tache]
        return capacite_restante
        
    def realisabilite(self,X):
        # Calcule la faisabilité totale de la solution
        deficit_total = 0
        for agent in range(self.m):
            capacite_agent = self.realisabilite_agent(agent, X)
            if capacite_agent < 0:
                deficit_total += capacite_agent
        return deficit_total


def sort_affectations(Pb):

    # Calcul des ratios de rentabilité (coût / ressource) pour chaque (agent, tâche)
    couples = []
    for i in range(Pb.m):
        for j in range(Pb.t):
            rentabilite = Pb.c[i][j] / Pb.r[i][j]
            couples.append(((i, j), rentabilite))
    # Tri des couples en fonction de la rentabilité décroissante
    couples_tries = sorted(couples, key=lambda x: x[1], reverse=True)
    return couples_tries   

def sol_gloutonne(Pb):
    couples_tries = sort_affectations(Pb)
    sol = [-1]*Pb.t
    assigned_tasks=0
    for couple in couples_tries:
        agent,tache = couple[0]
        if (sol[tache] == -1) and (Pb.realisabilite_agent(agent,sol) - Pb.r[agent][tache] >= 0):
            sol[tache] = agent
            assigned_tasks +=1
        if assigned_tasks == Pb.t:
            break
    return sol
    
def est_complete(X):
    # Vérifie si toutes les tâches sont affectées
    return all(x != -1 for x in X)

def sol_gloutonne_stoch(Pb):
    couples_tries = sort_affectations(Pb) # tester non trié ?
    sol = [-1]*Pb.t
    i=0

    for couple in couples_tries:
        agent,tache = couple[0]
        if (sol[tache] == -1) and (Pb.realisabilite_agent(agent,sol) - Pb.r[agent][tache] >= 0) and alpha>random.random():
            sol[tache] = agent
            i +=1
        if i == Pb.t:
            break
    return sol

def sol_gloutonne_stoch_complete(Pb):
    sol = sol_gloutonne_stoch(Pb)
    while not est_complete(sol):
        sol = sol_gloutonne_stoch(Pb)
    return sol

def fam_sols(Pb):
    N=40
    N = 40
    solutions_famille = [sol_gloutonne_stoch_complete(Pb) for _ in range(N)]
    return solutions_famille


"""Pb1 =  Pb("instances/gap1.txt",0)
sols_fam = fam_sols(Pb1)
for i in range(40):
    print(sols_fam[i], Pb1.evaluate(sols_fam[i]))
print(np.mean([Pb1.evaluate(sols_fam[i]) for i in range(40)]))"""

