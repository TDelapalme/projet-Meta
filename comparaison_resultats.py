import pandas as pd
import os
import ast
import numpy as np

# fichier pour extraire les résultats, les comparer à la valeur optimale et enregistrer.

global df_val_opt
df_val_opt = pd.read_csv("val_opt.csv")
def get_val_opt(df, instance, id, t, m):
    ligne_val = df[(df['instance'] == instance) & (df['id'] == id) & (df['t'] == t)& (df['m'] == m)]
    return ligne_val["val"].iloc[0]

def resultat(path, file, crit):
    """La fonction lit le fichier de résultat file et en crée un nouveau pour donner les resultats du rapport."""
    df = pd.read_csv(path + file)
    output = []
    for index, row in df.iterrows():
        instance = row["instance"]
        id = row["id"]
        t = row["t"]
        m = row["m"]
        val = row["val"]
        temps = round(row["time"],3)
        if crit=='max':
            t = 30
            m = 10
        v_opt = get_val_opt(df_val_opt, instance, id, t, m)
        if val == -1:
            val = np.nan
        if crit =='max':
            saut = v_opt - val
        else:
            saut = val-v_opt
        erreur = round(saut/v_opt*100,2)
        t = row["t"]
        m = row["m"]
        if crit == 'max':
            nom_instance = "c"+str(m)+str(t)+"-"+str(id+1)
        elif instance[-1] in ['a','b','c','d']:
            nom_instance = instance[-1]+str(m)+"-"+str(t)
        else:
            nom_instance= instance
        output.append({"instance":nom_instance,
                                "id":id,
                                "val":val,
                                "saut":saut,
                                "erreur":erreur,
                                "temps":temps,
                                "val opt":v_opt})
    res = pd.DataFrame(output)

    res.to_csv("./resultats/comparaison_borne/comp_"+file)
    print(file)

if __name__=='__main__':

    file_res_max = ['max_resultats-1-12_rl_depMult_reaffect_stoch_50_5.csv',
                    'max_resultats-1-12_rt_depMult_reaffect_stoch_4_tache_480_9.csv']
    file_res_min = ['min_resultats-a-c_rl_depMult_reaffect_stoch_50_5.csv',
                    'min_resultats-a-c_rt_depMult_reaffect_stoch_4_tache_480_60.csv',
                    'min_resultats-a-c_rt_depMult_reaffect_stoch_4_tache_480_9.csv',
                    'min_resultats-d_rl_depMult_reaffect_stoch_50_5.csv',
                    'min_resultats-d_rt_depMult_intDiv_reaffect_stoch_4_tache_480_9.csv',
                    'min_resultats-d_rt_depMult_reaffect_stoch_4_tache_480_60.csv',
                    'min_resultats_bonus_rl_depMult_reaffect_stoch_50_5.csv',
                    'min_resultats_bonus_rt_reaffect_stoch_360_120.csv']
    
    for file in file_res_max:
        resultat("resultats/",file, 'max')
    for file in file_res_min:
        resultat("resultats/",file, 'min')




    

            


        