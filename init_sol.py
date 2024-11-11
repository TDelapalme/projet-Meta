import readfiles
import random
import numpy as np
from concurrent.futures import ProcessPoolExecutor
import copy


# Param
alpha = 0.4

# une solution x est une liste de taille T le nb de tâches. 
# x[t] contient la valeur de la machine à laquelle t est affectée. si x[t] = -1 c'est que la tâche n'est pas affectée.
class Pb:

    def __init__(self, file, id) -> None:

        self.file = file
        self.id = id
        self.r, self.c, self.b, self.m, self.t = readfiles.readfile(file,id)
        self.x = -np.ones(self.t, dtype=int)
        self.b_res = np.copy(self.b)
        self.f = 0
    
    def eval(self):
        self.f = np.sum([self.c[self.x[t],t] for t in range(self.t)])
        return self.f
    
    def evaluate(self,X):
        f = 0
        for tache in range(len(X)):
            a = X[tache]
            f += self.c[a,tache]
        self.f = f
        return f
    
    def realisabilite_agent(self, agent, X):
        # Vérifie si un agent peut effectuer les tâches qui lui sont assignées
        capacite_restante = self.b[agent]
        for tache in range(self.t):
            if X[tache] == agent:
                capacite_restante -= self.r[agent][tache]
        return capacite_restante
    
    def capacites_residuelles(self):
        # maj des capacités résiduelles.
        for agent in range(self.m):
            self.b_res[agent] = self.realisabilite_agent(agent, self.x)
        return None
        
    def realisabilite(self,X):
        # Calcule la faisabilité totale de la solution
        deficit_total = 0
        for agent in range(self.m):
            capacite_agent = self.realisabilite_agent(agent, X)
            if capacite_agent < 0:
                deficit_total += capacite_agent
        return deficit_total


def sort_affectations_crit(Pb, critere = 'max'):

    # Calcul des ratios de rentabilité (coût / ressource) pour chaque (agent, tâche)
    couples = []
    for i in range(Pb.m):
        for j in range(Pb.t):
            rentabilite = Pb.c[i][j] / Pb.r[i][j]
            cr = Pb.c[i][j] * Pb.r[i][j]
            couples.append(((i, j), rentabilite, cr))
    # Si on cherche un max : Tri des couples en fonction de la rentabilité décroissante
    if critere == 'max':
        couples_tries = sorted(couples, key=lambda x: x[1], reverse=True)
    # Si on cherche un min : Tri des couples en fonction de r*c croissant 
    else :
        couples_tries = sorted(couples, key=lambda x: x[2], reverse=False)

    return couples_tries  

def sol_gloutonne(Pb):
    couples_tries = sort_affectations_crit(Pb)
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
    
def sol_gloutonne_2(Pb, critere = 'max'):
    # plus efficace que sol_gloutonne mais même principe.
    # retourne la solution
    couples_tries = sort_affectations_crit(Pb, critere)
    assigned_tasks=0
    for couple in couples_tries:
        agent,tache = couple[0]
        if (Pb.x[tache] == -1) and (Pb.b_res[agent] - Pb.r[agent][tache] >= 0):
            Pb.x[tache] = agent
            Pb.b_res[agent] = Pb.b_res[agent] - Pb.r[agent][tache]
            assigned_tasks +=1
        if assigned_tasks == Pb.t:
            break
    Pb.eval()
    Pb.capacites_residuelles()
    return (Pb.realisabilite(Pb.x)==0 and est_complete(Pb.x))

def est_complete(X):
    # Vérifie si toutes les tâches sont affectées
    return all(x != -1 for x in X)

def sol_gloutonne_stoch_backtrack(Pb, sol, sorted_affectations):

    # Si toutes les variables sont assignées, retourner la solution
    if est_complete(sol):
        return sol

    unassigned_tasks = [i for i in range(Pb.t) if sol[i]==-1]

    task = np.random.choice(unassigned_tasks)

    agent_values = [affectations[0][0] for affectations in sorted_affectations if affectations[0][1]==task]

    for a in agent_values:
        # On essaye une affectation
        if (Pb.realisabilite_agent(a, sol) - Pb.r[a][task] >= 0):
            sol[task] = a

            #print(f"Branchement : {task}={a}")

            # Recursive backtracking with changes tracked
            result = sol_gloutonne_stoch_backtrack(Pb, sol, sorted_affectations)
            
            if result:  # Si une solution est trouvée, la retourner
                return result

            #print('Echec backtrack')
            sol[task] = -1
    #print(f"Pas de valeur consitante pour {task}")
    return None
     


def sol_gloutonne_stoch_4(Pb, critere = 'max'):

    # On bruite la liste trié pour obtenir des solutions différentes à chaque appel
    alpha = 0.1
    sorted_affectations = sort_affectations_crit(Pb, critere)
    for i in range(len(sorted_affectations)-1):
        if random.random()>alpha:
            b = sorted_affectations[i]
            sorted_affectations[i] = sorted_affectations[i+1]
            sorted_affectations[i+1] = b

    t = Pb.t
    sol = [-1] * t
    return sol_gloutonne_stoch_backtrack(Pb, sol, sorted_affectations)

def sol_gloutonne_stoch_c(Pb, critere = "max"):
    sol = sol_gloutonne_stoch_4(Pb, critere)
    if type(sol)==type(None):
        Pb.f = -1
        return False
    else:
        Pb.x = sol
        Pb.eval()
        return True
    
def fam_sols(Pb, critere, N):
    with ProcessPoolExecutor() as executor:
        futures = [executor.submit(sol_gloutonne_stoch_4, Pb, critere) for _ in range(N)]
        solutions_famille = [future.result() for future in futures]
        
    return solutions_famille

if __name__=="__main__":
    # permet de lancer le code qui suit que si le fichier est exécuté (et pas s'il est importé)
    Pb1 =  Pb("instances/gapc.txt",0)
    sol = sol_gloutonne_2(Pb1,'min')
    print(Pb1.evaluate(sol))
    N = 20
    sols_fam = fam_sols(Pb1,'min',N)
    for i in range(N):
        print(sols_fam[i])
        print(Pb1.evaluate(sols_fam[i]))
    print(np.min([Pb1.evaluate(sols_fam[i]) for i in range(N)]))
