# Projet métaheuristiques

Tadeo Delapalme
Dimitri Delpech de Saint Guilhem

Ce projet implémente divers heuristiques pour le problème d'affectation généralisée.
- une solution gloutonne déterministe.
- une solution gloutonne stochastique.
- recherche locale (montee/descente) pour deux structures de voisinages.
- recherche taboue (basique, diversification, intensification) pour ces mêmes voisinages.
- algorithme mmémétique utilisant la recherche taboue.

## Architecture du dépôt:
### Dossiers
- instances : regroupe les divers instances du projet
- resultats : regroupe les résultats produits par res_rl_rt.ipynb pour la recherche locale et la recherche taboue
    - comparaison_borne: les fichiers de résultats pour ceux présentés dans le rapport

### Code
- init_sol.py: 
    - code la classe Pb qui code une instance du problème ainsi qu'une solution et sa valeur.
    - implémente les algorithmes gloutons
- voisinage.py: 
    - implémente les algorithmes de recherche locale selon différents critères
    - propose deux voisinages: la réaffectation d'une tâche ou la permutation de deux tâches.
- recherche_taboue.py:
    - implémente divers algorithmes de recherche taboue pour ces mêmes voisinages.
    - différents critères de liste taboue
    - avec ou sans diversification ou intensification
- operations_algo_genetique.py

- res_rl_rt.ipynb: notebook pour exécuter la recherche locale et taboue sur les instances.
- comparaison_borne.py: compare les résultats produits par res_rl_rt.ipynb avec leur valeur optimale.
- readfiles.py: permet de lire les instances.

