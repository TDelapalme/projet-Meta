import numpy as np

def readfile(fname, id):
    
    with open(fname, 'r') as f:
        lines = f.readlines()
    
    # Le nombre d'instances est sur la première ligne
    nbInst = int(lines[0].strip())
    
    # Vérification que l'ID d'instance est valide
    assert id < nbInst, "ID d'instance invalide"
    
    deb = 1
    
    for i in range(id + 1):
        # Lire m et t pour cette instance
        m, t = map(int, lines[deb].strip().split())
        
        deb_c_start = deb + 1
        deb_r_start = deb_c_start + m
        deb_b_start = deb_r_start + m
        
        if i == id:
            c = np.array([list(map(int, lines[j].strip().split())) for j in range(deb_c_start, deb_r_start)])
            r = np.array([list(map(int, lines[j].strip().split())) for j in range(deb_r_start, deb_b_start)])
            b = np.array(list(map(int, lines[deb_b_start].strip().split())))
        
        deb = deb_b_start + 1
    
    return(r, c, b, m, t)
