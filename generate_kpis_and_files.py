import json
import pandas as pd
import numpy as np

with open('quotidien.geojson') as fp:
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

list_fuels = ["SP95", "E10", "SP98", "Gazole", "GPLc", "E85"]

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
        if r["debut"] > "2022-09-15":
            mydict["properties"][r["nom"]] = "R"
        else:
            mydict["properties"][r["nom"]] = "N"
            
        mydict["properties"][r["nom"] + "_s"] = r["debut"]
        mydict["properties"][r["nom"] + "_m"] = None

    for p in d["properties"]["prix"]:
        mydict["properties"][p["nom"]] = p["valeur"]
        mydict["properties"][p["nom"] + "_s"] = None
        mydict["properties"][p["nom"] + "_m"] = p["maj"]
    
    for fuel in list_fuels:
        if fuel not in mydict["properties"]:
            mydict["properties"][fuel] = "N"
            mydict["properties"][fuel + "_s"] = None
            mydict["properties"][fuel + "_m"] = None

    mydict["geometry"] = d["geometry"]
    obj["features"].append(mydict)

arr = []
geometries = {}
for d in obj["features"]:
    mydict = d["properties"]
    arr.append(mydict)

df = pd.DataFrame(arr)

df = df.where(pd.notnull(df), None)

with open("latest.geojson") as fp:
    data = json.load(fp)

final = {}
final["type"] = "FeatureCollection"
final["features"] = []
for d in data["features"]:
    for p in d["properties"]["prix"]:
        df.loc[df["id"] == d["properties"]["id"], p["nom"] + "_m"] = p["maj"]
        df.loc[df["id"] == d["properties"]["id"], p["nom"]] = p["valeur"]
    mydict = {}
    mydict["type"] = "Feature"
    dfinter = df[df["id"] == d["properties"]["id"]]
    if dfinter.shape[0] > 0:
        mydict["properties"] = dfinter.to_dict(orient="records")[0]
    else:
        mydict["properties"] = {}
    mydict["geometrey"] = d["geometry"]
    final["features"].append(mydict)
        
tab = {
    "SP95": 0,
    "SP95r": 0,
    "SP95v": [],
    "SP98": 0,
    "SP98r": 0,
    "SP98v": [],
    "E10": 0,
    "E10r": 0,
    "E10v": [],
    "Gazole": 0,
    "Gazoler": 0,
    "Gazolev": [],
    "E85": 0,
    "E85r": 0,
    "E85v": [],
    "GPLc": 0,
    "GPLcr": 0,
    "GPLcv": []
}

for f in final["features"]:
    for fuel in list_fuels:
        if fuel in f["properties"]:
            if f["properties"][fuel] not in ["R", "N"]:
                tab[fuel] = tab[fuel] + 1
                tab[fuel + "v"].append(float(f["properties"][fuel]))
            elif f["properties"][fuel] == "R":
                tab[fuel + "r"] = tab[fuel + "r"] + 1

final["properties"] = {}
for fuel in list_fuels:
    
    final["properties"][fuel] = [
        np.min(tab[fuel + "v"]),
        round(np.quantile(tab[fuel + "v"], .333333),2),
        round(np.quantile(tab[fuel + "v"], .66666),2),
        np.max(tab[fuel + "v"])
    ]
    final["properties"][fuel + "_mean"] = np.mean(tab[fuel + "v"])
    final["properties"][fuel + "_median"] = np.median(tab[fuel + "v"])
    final["properties"][fuel + "_rupture"] = round((tab[fuel + "r"] / (tab[fuel + "r"] + tab[fuel]) * 100), 2)

def getColor(val, fuel):
    if fuel == "SP95":
        arr = final["properties"]["SP95"]
    if fuel == "SP98":
        arr = final["properties"]["SP98"]
    if fuel == "E10":
        arr = final["properties"]["E10"]
    if fuel == "Gazole":
        arr = final["properties"]["Gazole"]
    if fuel == "GPLc":
        arr = final["properties"]["Gazole"]
    if fuel == "E85":
        arr = final["properties"]["Gazole"]
    if val < arr[1]:
        return "1"
    if val < arr[2]:
        return "2"
    if val >= arr[2]:
        return "3"

for d in final["features"]:
    for fuel in list_fuels:
        if fuel in d["properties"]:
            if d["properties"][fuel] == "R":
                d["properties"][fuel + "_color"] = "0"
            elif d["properties"][fuel] == "N":
                d["properties"][fuel + "_color"] = "-1"
            else:
                d["properties"][fuel + "_color"] = getColor(float(d["properties"][fuel]), fuel)

with open("latest_france.geojson", "w") as fp:
    json.dump(final, fp)
