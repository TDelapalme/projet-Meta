import readfiles

class Pb:

    def __init__(self, file, id) -> None:
        self.file = file
        self.id = id
        self.r, self.c, self.b, self.m, self.t = readfiles.readfile(file,1)
        self.X = [-1]*self.t

    def evaluate(self):
        f = 0
        for tache in range(len(self.X)):
            a = self.X[tache]
            f += self.c[a,tache]
        return f
    
    def realisabilite_agent(self,a):
        S_taches_M = self.b[a]
        for tache in range(self.t):
            S_taches_M += -self.r[a][tache]*self.X[tache]
        return S_taches_M
    
    def realisabilite(self):
        """Sommes des réalisabilité < 0, ie des contraintes violées

        Returns:
            S: Sommes des réalisabilité < 0
        """
        S = 0
        for a in range(self.m):
            sa = self.realisabilite_agent(a)
            if sa < 0:
                S += sa
        return S
    
    def affectation_mt(self):
        return None
    

def sort_affectations(Pb):

    rentabilité = [[0]*Pb.t]*Pb.m
    couples = []

    for i in range(Pb.m):
        for j in range(Pb.t):
            rentabilité[i][j] = Pb.c[i][j]/Pb.r[i][j]
            couples.append(((i,j),rentabilité[i][j]))

    couples_tries = sorted(couples, key=lambda x: x[1], reverse=True)

    return couples_tries   

def sol_gloutonne(Pb):

    couples_tries = sort_affectations(Pb)
    sol = Pb.X
    i=0

    for couple in couples_tries:
        agent,tache = couple[0]
        if (sol[tache] == -1) and (Pb.realisabilite_agent(agent) >= 0):
            sol[tache] = agent
            i +=1
        if i == Pb.t:
            break
    print(i)
    return sol
    
Pb1 =  Pb("instances/gap1.txt",0)
#print(Pb1.sort_affectations())
#print(Pb1.evaluate())
print(sol_gloutonne(Pb1))