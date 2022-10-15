import json
import pandas as pd

with open('latest.geojson') as fp:
    data = json.load(fp)

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

def process_geojson(fuel, type_file, arr):
    obj = {}
    obj["type"] = "FeatureCollection"
    obj["features"] = []
    for d in data['features']:
        mydict = {}
        mydict["type"] = "Feature"
        mydict["properties"] = {}
        for rupt in d["properties"]["ruptures"]:
            if type_file == "ruptures":
                if rupt["nom"] == fuel and rupt["debut"] > "2022-09-15":
                    mydict["properties"] = {
                        "id": d["properties"]["id"],
                        "dep": parseCP(d["properties"]["cp"]),
                        "debut": rupt["debut"]
                    }
                    mydict["geometry"] = d["geometry"]
                    obj["features"].append(mydict)
                    
                    mydict = {}
                    mydict["dep"] = parseCP(d["properties"]["cp"])
                    mydict["fuel"] = fuel
                    mydict["type"] = "rupture"
                    arr.append(mydict)
        for prix in d["properties"]["prix"]:
            if type_file == "prix":
                if prix["nom"] == fuel:
                    mydict["properties"] = {
                        "id": d["properties"]["id"],
                        "dep": parseCP(d["properties"]["cp"]),
                        "maj": prix["maj"],
                        "val": prix["valeur"]
                    }
                    mydict["geometry"] = d["geometry"]
                    obj["features"].append(mydict)
                    mydict = {}
                    mydict["dep"] = parseCP(d["properties"]["cp"])
                    mydict["fuel"] = fuel
                    mydict["type"] = "prix"
                    mydict["prix"] = prix["valeur"]
                    arr.append(mydict)
    return obj, arr
                
arr = []
for fuel in ["SP95", "SP98", "Gazole"]:
    for type_file in ["ruptures", "prix"]:
        toDump, arr = process_geojson(fuel, type_file, arr)
        with open(fuel + "_" + type_file + ".json", "w") as fp:
            json.dump(toDump, fp)

df = pd.DataFrame(arr)
df = df[df["dep"] != "99"]
df["count"] = 1

agg = df.groupby(["dep", "fuel", "type"], as_index=False).count()
agg[(agg["fuel"] == "SP95") & (agg["type"] == "rupture")]

for fuel in ["Gazole", "SP95", "SP98"]:
    for dep in df.dep.unique():
        if agg[(agg["dep"] == dep) & (agg["type"] == "rupture") & (agg["fuel"] == fuel)].shape[0] == 0:
            print(dep, fuel)
            agg = agg.append({'dep':dep, 'fuel':fuel, 'type':'rupture', 'count': 0}, ignore_index=True)

def get_pourcentage(row, df):
    return round(row["count"] / df[(df["fuel"] == row["fuel"]) & (df["dep"] == row["dep"])]["count"].sum() * 100, 2)

agg["valeur"] = agg.apply(lambda row: get_pourcentage(row, df), axis=1)

for fuel in ["Gazole", "SP95", "SP98"]:
    res = agg[(agg["fuel"] == fuel) & (agg["type"] == "rupture")][["dep", "valeur"]]
    res = res[res["valeur"].notna()]
    with open(fuel + "_ruptures_synthese_dep.json", "w") as fp:
        json.dump(res.to_dict(orient="records"), fp)


df["prix"] = df["prix"].astype(float)

agg = df[["dep", "fuel", "prix"]][df["type"] == "prix"].groupby(["dep", "fuel"], as_index=False).median()

agg = agg.rename(columns={"prix": "valeur"})

for fuel in ["Gazole", "SP95", "SP98"]:
    res = agg[(agg["fuel"] == fuel)][["dep", "valeur"]]
    with open(fuel + "_prix_mediane_dep.json", "w") as fp:
        json.dump(res.to_dict(orient="records"), fp)