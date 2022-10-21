import json
import pandas as pd
import numpy as np

with open('latest.geojson') as fp:
    data = json.load(fp)
    
listdates = []
for d in data["features"]:
    for p in d["properties"]["prix"]:
        listdates.append(p["maj"][:10])

listdates = (list(dict.fromkeys(listdates)))
listdates.sort()

list_fuels = ["Gazole", "SP95", "SP98", "E10", "GPLc", "E85"]

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

for mydate in listdates:
    print(mydate)
    if(mydate > "2022-10-15"):
        valsp98 = []
        valsp95 = []
        vale10 = []
        valgaz = []
        valgplc = []
        vale85 = []

        valsp98r = []
        valsp95r = []
        vale10r = []
        valgazr = []
        valgplcr = []
        vale85r = []

        dates = []

        obj = {}
        obj["type"] = "FeatureCollection"
        obj["features"] = []
        for d in data['features']:
            toPush = False
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
                if mydate >= "2022-09-15" and r["debut"] > "2022-09-15":
                    mydict["properties"][r["nom"]] = "R"
                    mydict["properties"][r["nom"] + "_since"] = r["debut"]

                    if r["nom"] == "SP95":
                        valsp95r.append(1)
                    if r["nom"] == "SP98":
                        valsp98r.append(1)
                    if r["nom"] == "E10":
                        vale10r.append(1)
                    if r["nom"] == "Gazole":
                        valgazr.append(1)
                    if r["nom"] == "GPLc":
                        valgplcr.append(1)
                    if r["nom"] == "E85":
                        vale85r.append(1)


            for p in d["properties"]["prix"]:
                if(mydate in p["maj"]):
                    dates.append(p["maj"])
                    toPush = True
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
                    if p["nom"] == "GPLc":
                        valgplc.append(float(p["valeur"]))
                    if p["nom"] == "E85":
                        vale85.append(float(p["valeur"]))

            mydict["geometry"] = d["geometry"]
            if toPush:
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


        obj["properties"]["GPLc"] = [
            np.min(valgplc),
            round(np.quantile(valgplc, .333333),2),
            round(np.quantile(valgplc, .66666),2),
            np.max(valgplc)
        ]
        obj["properties"]["GPLc_mean"] = np.mean(valgplc)
        obj["properties"]["GPLc_median"] = np.median(valgplc)
        obj["properties"]["GPLc_rupture"] = round((len(valgplcr) / (len(valgplcr) + len(valgplc)))*100,2)


        obj["properties"]["E85"] = [
            np.min(vale85),
            round(np.quantile(vale85, .333333),2),
            round(np.quantile(vale85, .66666),2),
            np.max(vale85)
        ]
        obj["properties"]["E85_mean"] = np.mean(vale85)
        obj["properties"]["E85_median"] = np.median(vale85)
        obj["properties"]["E85_rupture"] = round((len(vale85r) / (len(vale85r) + len(vale85)))*100,2)


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
            if fuel == "GPLc":
                arr = obj["properties"]["GPLc"]
            if fuel == "E85":
                arr = obj["properties"]["E85"]
            if val < arr[1]:
                return "1"
            if val < arr[2]:
                return "2"
            if val >= arr[2]:
                return "3"

        for d in obj["features"]:
            for fuel in ["SP95", "Gazole", "E10", "SP98", "GPLC", "E85"]:
                if fuel in d["properties"]:
                    if d["properties"][fuel] == "R":
                        d["properties"][fuel + "_color"] = "0"
                    elif d["properties"][fuel] == "N":
                        d["properties"][fuel + "_color"] = "-1"
                    else:
                        d["properties"][fuel + "_color"] = getColor(float(d["properties"][fuel]), fuel)


        with open(mydate + ".json", "w") as fp:
            json.dump(obj, fp)

