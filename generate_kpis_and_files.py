import json
import pandas as pd
import numpy as np

with open('latest.geojson') as fp:
    data = json.load(fp)

list_fuels = ["Gazole", "SP95", "SP98", "E10"]

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


valsp98 = []
valsp95 = []
vale10 = []
valgaz = []

valsp98r = []
valsp95r = []
vale10r = []
valgazr = []

dates = []

obj = {}
obj["type"] = "FeatureCollection"
obj["features"] = []
for d in data['features']:
    mydict = {}
    mydict["type"] = "Feature"
    mydict["properties"] = {}
    mydict["properties"]["id"] = d["properties"]["id"]
    mydict["properties"]["adr"] = (
        d["properties"]["adresse"].encode('Latin-1', 'ignore').decode('utf-8').lower()
    )
    mydict["properties"]["cpl_adr"] = (
        d["properties"]["cp"].encode('Latin-1', 'ignore').decode('utf-8').lower()
        + " " + d["properties"]["ville"].encode('Latin-1', 'ignore').decode('utf-8').lower()
    )
    mydict["properties"]["dep"] = parseCP(d["properties"]["cp"])
    for r in d["properties"]["ruptures"]:
        if r["debut"] > "2022-09-15":
            mydict["properties"][r["nom"]] = "R"
            mydict["properties"][r["nom"] + "_since"] = r["debut"]
            
        if p["nom"] == "SP95":
            valsp95r.append(mydict["properties"][r["nom"]])
        if p["nom"] == "SP98":
            valsp98r.append(mydict["properties"][r["nom"]])
        if p["nom"] == "E10":
            vale10r.append(mydict["properties"][r["nom"]])
        if p["nom"] == "Gazole":
            valgazr.append(mydict["properties"][r["nom"]])


    for p in d["properties"]["prix"]:
        dates.append(p["maj"])
        mydict["properties"][p["nom"]] = p["valeur"]
        mydict["properties"][p["nom"] + "_maj"] = p["maj"]
        
        if p["nom"] == "SP95":
            valsp95.append(float(p["valeur"]))
        if p["nom"] == "SP98":
            valsp98.append(float(p["valeur"]))
        if p["nom"] == "E10":
            vale10.append(float(p["valeur"]))
        if p["nom"] == "Gazole":
            valgaz.append(float(p["valeur"]))

            
    mydict["geometry"] = d["geometry"]
    obj["features"].append(mydict)
            
    
obj["properties"] = {}
obj["properties"]["SP95"] = [
    np.min(valsp95),
    round(np.quantile(valsp95, .333333),2),
    round(np.quantile(valsp95, .66666),2),
    np.max(valsp95)
]
obj["properties"]["SP95_mean"] = np.mean(valsp95)
obj["properties"]["SP95_median"] = np.median(valsp95)
obj["properties"]["SP95_rupture"] = round((len(valsp95r) / (len(valsp95r) + len(valsp95)))*100,2)


obj["properties"]["SP98"] = [
    np.min(valsp98),
    round(np.quantile(valsp98, .333333),2),
    round(np.quantile(valsp98, .66666),2),
    np.max(valsp98)
]
obj["properties"]["SP98_mean"] = np.mean(valsp98)
obj["properties"]["SP98_median"] = np.median(valsp98)
obj["properties"]["SP98_rupture"] = round((len(valsp98r) / (len(valsp98r) + len(valsp98)))*100,2)

obj["properties"]["E10"] = [
    np.min(vale10),
    round(np.quantile(vale10, .333333),2),
    round(np.quantile(vale10, .66666),2),
    np.max(vale10)
]
obj["properties"]["E10_mean"] = np.mean(vale10)
obj["properties"]["E10_median"] = np.median(vale10)
obj["properties"]["E10_rupture"] = round((len(vale10r) / (len(vale10r) + len(vale10)))*100,2)

obj["properties"]["Gazole"] = [
    np.min(valgaz),
    round(np.quantile(valgaz, .333333),2),
    round(np.quantile(valgaz, .66666),2),
    np.max(valgaz)
]
obj["properties"]["Gazole_mean"] = np.mean(valgaz)
obj["properties"]["Gazole_median"] = np.median(valgaz)
obj["properties"]["Gazole_rupture"] = round((len(valgazr) / (len(valgazr) + len(valgaz)))*100,2)

obj["properties"]["maj"] = max(dates)

def getColor(val, fuel):
    if fuel == "SP95":
        arr = obj["properties"]["SP95"]
    if fuel == "SP98":
        arr = obj["properties"]["SP98"]
    if fuel == "E10":
        arr = obj["properties"]["E10"]
    if fuel == "Gazole":
        arr = obj["properties"]["Gazole"]
    if val < arr[1]:
        return "1"
    if val < arr[2]:
        return "2"
    if val >= arr[2]:
        return "3"

for d in obj["features"]:
    for fuel in ["SP95", "Gazole", "E10", "SP98"]:
        if fuel in d["properties"]:
            if d["properties"][fuel] == "R":
                d["properties"][fuel + "_color"] = "0"
            else:
                d["properties"][fuel + "_color"] = getColor(float(d["properties"][fuel]), fuel)


with open("synthese_france.json", "w") as fp:
    json.dump(obj, fp)

