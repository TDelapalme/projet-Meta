import pandas as pd
import os
import ast
import numpy as np

def lire_valeur(s, cle = 'val'):
    # Convertir la chaîne en dictionnaire
    try:
        data = ast.literal_eval(s)
        # Retourner la valeur associée à 'val'
        return data.get(cle)
    except (ValueError, SyntaxError):
        return None
    

instances = ["gap1","gap2", "gap3","gap4","gap5","gap6","gap7","gap8","gap9","gap10","gap11","gap12"]


if __name__=='__main__':
    val_opt = pd.read_csv("val_opt.csv")
    for file in os.listdir():
        
        if file[-4:]==".csv" and file != "val_opt.csv":
            res = pd.read_csv(file)
            res_pd = pd.DataFrame()
            res_df = pd.DataFrame(columns=['file', 'id', 'val', 'saut', 'erreur', 'temps', 'val opt'])
            index = 0
            for instance in instances:
                for i in range(5):
                    v_opt = lire_valeur(val_opt[instance][i])
                    val = lire_valeur(res[instance][i])
                    if val == -1:
                        val = np.nan
                    saut = v_opt - val
                    erreur = saut/v_opt
                    temps = lire_valeur(res[instance][i], cle='time')
                    nv_ligne = {"file":instance,
                                "id":i,
                                "val":val,
                                "saut":saut,
                                "erreur":erreur,
                                "temps":temps,
                                "val opt":v_opt}
                    res_df.loc[index] = nv_ligne
                    index +=1

            res_df.to_csv("./resultats/complet_"+file)
            print(file, "\t\t",res_df["erreur"].mean())


            


        