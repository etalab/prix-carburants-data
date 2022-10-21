#!/bin/bash

rm -rf /tmp/prix-carburants
mkdir -p /tmp/prix-carburants
cd /tmp/prix-carburants
git clone git@github.com:etalab/prix-carburants-data.git
cp prix-carburants-data/generate_kpis_and_files.py .
cp prix-carburants-data/reformat-prix-carburants.py .
wget -P /tmp/prix-carburants --content-disposition https://donnees.roulez-eco.fr/opendata/jour
tmp=(*.zip)
filename=${tmp[0]}
mydate=${filename:0-12}
mydate=${mydate:0:8}
7z x $filename
tmp=(*.xml)
filename=${tmp[0]}
iconv -f iso-8859-1 -t utf-8 $filename >| $mydate".xml"
rm -rf $filename
python reformat-prix-carburants.py $mydate".xml"
rm -rf *.zip
rm -rf *.xml
mv latest.geojson quotidien.geojson

wget -P /tmp/prix-carburants --content-disposition https://donnees.roulez-eco.fr/opendata/instantane
tmp=(*.zip)
filename=${tmp[0]}
mydate=$(date +"%Y-%m-%d")
7z x $filename
tmp=(*.xml)
filename=${tmp[0]}
iconv -f iso-8859-1 -t utf-8 $filename >| $mydate".xml"
rm -rf $filename
python reformat-prix-carburants.py $mydate".xml"
rm -rf *.zip
rm -rf *.xml
python generate_kpis_and_files.py

git config --global user.email "airflow@etalab.com"
git config --global user.name "Airflow"
rm -rf latest.geojson
rm -rf quotidien.geojson

mkdir $mydate
cp -r latest_france.json /tmp/prix-carburants/prix-carburants-data/dist/historique/$mydate.json
cp -r latest_france.json /tmp/prix-carburants/prix-carburants-data/dist/latest_france.json
cd /tmp/prix-carburants/prix-carburants-data/

if [ -n "$(git status --porcelain)" ]; then
    git add dist
    git commit -am "New data at $(date -u +'%Y-%m-%dT%H:%M:%SZ')"
    git push origin master
else
    echo "No changes";
fi