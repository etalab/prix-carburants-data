import json
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta

def is_rupture_essence(row):
    if row["SP95"] == "R" and row["E10"] != "S" and row["SP98"] != "S":
        return "R"
    if row["SP95"] != "S" and row["E10"] == "R" and row["SP98"] != "S":
        return "R"
    if row["SP95"] != "S" and row["E10"] != "S" and row["SP98"] == "R":
        return "R"
    if row["SP95"] != "ND":
        return "S"
    if row["E10"] != "ND":
        return "S"
    if row["SP98"] != "ND":
        return "S"
    return "ND"


def rupture_au_moins_un_produit(row):
    if row["essence"] == "R" or row["Gazole"] == "R":
        return "R"
    if row["essence"] == "ND" and row["Gazole"] == "ND":
        return "ND"
    return "S"


def rupture_deux_produits(row):
    if row["essence"] == "R" and row["Gazole"] == "R":
        return "R"
    if row["essence"] == "ND" and row["Gazole"] == "ND":
        return "ND"
    return "S"


def parseCP(val):
    if val[:2] == "97":
        return val[:3]
    if val[:3] == "200" or val[:3] == "201":
        return "2A"
    if val[:3] == "202" or val[:3] == "206":
        return "2B"
    if val[:2] == "20" and val[:3] != "200" and val[:3] != "202":
        print(val)
    else:
        return val[:2]


def get_stats_df(df):
    arr = []
    for lf in list_fuels:
        for d in df["dep"].unique():
            mydict = {}
            mydict["dep"] = d
            mydict["carburant"] = lf
            try:
                mydict["pourcentage_rupture"] = df[(df["dep"] == d) & \
                                                        (df["carburant"] == lf) & \
                                                        (df["etat"] == "R")]["nb"].iloc[0] / \
                                                (
                                                 df[(df["dep"] == d) & \
                                                        (df["carburant"] == lf) & \
                                                        (df["etat"] == "R")]["nb"].iloc[0] + \
                                                 df[(df["dep"] == d) & \
                                                        (df["carburant"] == lf) & \
                                                        (df["etat"] == "S")]["nb"].iloc[0]
                                                ) * 100
            except:
                mydict["pourcentage_rupture"] = 0
            mydict["nombre_rupture"] = df[(df["dep"] == d) & \
                                                        (df["carburant"] == lf) & \
                                                        (df["etat"] == "R")]["nb"].iloc[0]
            mydict["nombre_stations"] = (
                                                 df[(df["dep"] == d) & \
                                                        (df["carburant"] == lf) & \
                                                        (df["etat"] == "R")]["nb"].iloc[0] + \
                                                 df[(df["dep"] == d) & \
                                                        (df["carburant"] == lf) & \
                                                        (df["etat"] == "S")]["nb"].iloc[0]
                                                )

            arr.append(mydict)
    return pd.DataFrame(arr)


list_fuels = ["SP95", "E10", "SP98", "Gazole", "GPLc", "E85"]

with open("quotidien.geojson") as fp:
    data = json.load(fp)

start_date_rupture = (datetime.today() - relativedelta(years=1)).strftime('%Y-%m-%d')

obj = {}
obj["type"] = "FeatureCollection"
obj["features"] = []
for d in data['features']:
    mydict = {}
    mydict["type"] = "Feature"
    mydict["properties"] = {}
    mydict["properties"]["id"] = d["properties"]["id"]
    mydict["properties"]["adr"] = (
        d["properties"]["adresse"].encode('Latin-1', 'ignore').decode('utf-8', 'ignore').lower()
    )
    mydict["properties"]["cpl_adr"] = (
        d["properties"]["cp"].encode('Latin-1', 'ignore').decode('utf-8', 'ignore').lower()
        + " " + d["properties"]["ville"].encode('Latin-1', 'ignore').decode('utf-8', 'ignore').lower()
    )
    mydict["properties"]["dep"] = parseCP(d["properties"]["cp"])
    for r in d["properties"]["ruptures"]:
        # old 2022-09-15
        if r["debut"] > start_date_rupture:
            mydict["properties"][r["nom"]] = "R"
        else:
            mydict["properties"][r["nom"]] = "ND"
            
        mydict["properties"][r["nom"] + "_prix"] = None
        mydict["properties"][r["nom"] + "_date"] = r["debut"]

    for p in d["properties"]["prix"]:
        mydict["properties"][p["nom"]] = "S"
        mydict["properties"][p["nom"] + "_prix"] = p["valeur"]
        mydict["properties"][p["nom"] + "_date"] = p["maj"]
    
    for fuel in list_fuels:
        if fuel not in mydict["properties"]:
            mydict["properties"][fuel] = "ND"
            mydict["properties"][fuel + "_prix"] = None
            mydict["properties"][fuel + "_date"] = None

    mydict["geometry"] = d["geometry"]
    obj["features"].append(mydict)


arr = []
geometries = {}
for d in obj["features"]:
    mydict = d["properties"]
    arr.append(mydict)

mef = pd.DataFrame(arr)
mef["essence"] = mef.apply(lambda row: is_rupture_essence(row), axis=1)
mef["au_moins_un_produit"] = mef.apply(lambda row: rupture_au_moins_un_produit(row), axis=1)
mef["deux_produits"] = mef.apply(lambda row: rupture_deux_produits(row), axis=1)

list_fuels = ["SP95", "E10", "SP98", "Gazole", "GPLc", "E85", "essence", "au_moins_un_produit", "deux_produits"]

id_mef = list(mef["id"].unique())

mef_dep = pd.DataFrame(columns=['dep','etat','nb','carburant'])

for lf in list_fuels:
    inter = mef[["dep", lf, "id"]].groupby(["dep", lf], as_index=False).count() \
    .rename(columns={"id": "nb", lf: "etat"})
    inter["carburant"] = lf
    mef_dep = pd.concat([mef_dep, inter])


for lf in list_fuels:
    for d in mef_dep["dep"].unique():
        if mef_dep[(mef_dep["dep"] == d) & (mef_dep["carburant"] == lf) & (mef_dep["etat"] == "R")].shape[0] == 0:
            new_row = {"dep": d, "etat": "R", "nb": 0, "carburant": lf}
            mef_dep = mef_dep.append(new_row, ignore_index=True)
        if mef_dep[(mef_dep["dep"] == d) & (mef_dep["carburant"] == lf) & (mef_dep["etat"] == "S")].shape[0] == 0:
            new_row = {"dep": d, "etat": "S", "nb": 0, "carburant": lf}
            mef_dep = mef_dep.append(new_row, ignore_index=True)

stats_mef_dep = get_stats_df(mef_dep)
deps = pd.read_csv("deps_regs.csv", dtype=str)
stats_mef_reg = pd.merge(stats_mef_dep, deps, on="dep", how="left")
stats_mef_reg = stats_mef_reg.groupby(["reg", "libelle_region", "carburant"], as_index=False).sum()
stats_mef_reg["pourcentage_rupture"] = round(stats_mef_reg["nombre_rupture"] / stats_mef_reg["nombre_stations"] * 100, 2)
stats_mef_nat = stats_mef_reg.groupby(["carburant"], as_index=False).sum()
stats_mef_nat["pourcentage_rupture"] = round(stats_mef_nat["nombre_rupture"] / stats_mef_nat["nombre_stations"] * 100, 2)
writer = pd.ExcelWriter('synthese_ruptures_latest.xlsx', engine='xlsxwriter')
stats_mef_dep.to_excel(writer, sheet_name='départements', index=False)
stats_mef_reg.to_excel(writer, sheet_name='régions', index=False)
stats_mef_nat.to_excel(writer, sheet_name='national', index=False)
writer.close()

df = stats_mef_dep
df.groupby(["dep", "carburant"], as_index=False).count()

arr = []
for d in df.dep.unique():
    mydict = {}
    mydict["dep"] = d
    for lf in list_fuels:        
        mydict[lf] = round(df[(df["dep"] == d) & (df["carburant"] == lf)]["pourcentage_rupture"].iloc[0],2)
        mydict[lf + "_nbrup"] = df[(df["dep"] == d) & (df["carburant"] == lf)]["nombre_rupture"].iloc[0]
        mydict[lf + "_nbstation"] = df[(df["dep"] == d) & (df["carburant"] == lf)]["nombre_stations"].iloc[0]
    arr.append(mydict)

res = pd.DataFrame(arr)

res.to_json("latest_france_ruptures.json", orient="records")
