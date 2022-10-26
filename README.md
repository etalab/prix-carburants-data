## Traitements des données prix des carburants

[Les données sources](https://www.data.gouv.fr/fr/datasets/prix-des-carburants-en-france-flux-instantane/) se trouvent sur data.gouv.fr

Toutes les 30minutes, un traitement récupère ce repo et execute le script shell `update.sh`

Celui-ci :
- télécharge les données (flux instantannée et flux quotidien)
- dézippe les fichiers
- convertit les xml en geojson grâce au script `reformat-prix-carburants.py`
- génère un fichier `latest_france.json` et un fichier `prix_2022.json` (dans le dossier dist) grâce au script `generate_kpis_and_files.py`

Ces fichiers de sortie sont directement utilisés par la visualisation présente sur https://explore.data.gouv.fr/prix-carburants
