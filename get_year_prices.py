from glob import glob


import glob
import json

files = glob.glob('./dist/historique/*')
files.sort()

arr = []
for f in files:
    print(f)
    with open(f, 'r') as fp:
        data = json.load(fp)
    mydate = f.replace('.json','')[-10:]
    mydate = mydate[:4] + "-" + mydate[5:7] + "-" + mydate[8:10]
    mydict = {}
    mydict["date"] = mydate 
    mydict["SP95_mean"] = data["properties"]["SP95_mean"]
    mydict["SP95_median"] = data["properties"]["SP95_median"]
    mydict["E10_mean"] = data["properties"]["E10_mean"]
    mydict["E10_median"] = data["properties"]["E10_median"]
    mydict["SP98_mean"] = data["properties"]["SP98_mean"]
    mydict["SP98_median"] = data["properties"]["SP98_median"]
    mydict["Gazole_mean"] = data["properties"]["Gazole_mean"]
    mydict["Gazole_median"] = data["properties"]["Gazole_median"]
    mydict["GPLc_mean"] = data["properties"]["GPLc_mean"]
    mydict["GPLc_median"] = data["properties"]["GPLc_median"]
    mydict["E85_mean"] = data["properties"]["E85_mean"]
    mydict["E85_median"] = data["properties"]["E85_median"]
    arr.append(mydict)

with open('./dist/prix_2022.json', 'w') as fp:
    json.dump(arr, fp)