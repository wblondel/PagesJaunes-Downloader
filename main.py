# !/usr/bin/python
# -*- coding: utf-8 -*-

# PagesJaunesScrap Copyright (C) 2017    William Gerald Blondel
# contact@williamblondel.fr
# Last modified 14th August 2017

import json
from pathlib import Path
from tqdm import tqdm
import requests
import datetime


DIRECTORIES_LIST_FILENAME = Path("liste_annuaires.json")
CHUNK_SIZE = 1024*1024

# We load the list of directories
with DIRECTORIES_LIST_FILENAME.open() as directories_list_fileobject:
    directories = json.load(directories_list_fileobject)["annuaires"]

# We ask the user which directory he wants to scrap
numAnnToScrap = None
annType = None
annYear = datetime.datetime.now().year

print("!!! ATTENTION !!!")
print("Les annuaires Pages Blanches des départements suivants ne sont plus disponibles, "
      "ni au format papier ni au format numérique :")
print("06, 13, 20, 30, 31, 33, 34, 38, 42, 44, 49, 57, 59, 60, 62, 64, 69, 74, 75, 76, 77, "
      "78, 83, 84, 91, 92, 93, 94, 95, 974, 975, 976")
print("Les éditions des années précédentes ne sont également plus disponibles.")
print()


while numAnnToScrap not in [item["numAnn"] for item in directories]:
    numAnnToScrap = input("Veuillez entrer le numéro du département dont vous voulez récupérer l'annuaire : ").zfill(3)

dptToScrap = [item for item in directories if item['numAnn'] == numAnnToScrap][0]
print(f"Vous avez choisi le département {dptToScrap['nomDpt']} ({dptToScrap['numAnn']}).")
print()

while annType not in ["pja", "anu"]:
    annType = input("Voulez-vous récupérer l'annuaire PagesJaunes (PJA) ou PagesBlanches (ANU) ? ").lower()

print(f"Vous avez choisi l'annuaire {annType}.")
print()

if annType == "pja" and len(dptToScrap) > 2:
    print("Ce département a plusieurs annuaires.")

    for subAnn in dptToScrap["sousAnn"]:
        print(f"> {subAnn['nomAnn']} ({subAnn['numAnn']})")

    print()

    while numAnnToScrap not in [item["numAnn"] for item in dptToScrap["sousAnn"]]:
        numAnnToScrap = input("Lequel voulez-vous récupérer ? ")

    print()
    print(f"Vous avez choisi l'annuaire {numAnnToScrap}.")
    print()


# We create the folder where the files will be downloaded
Path(f"{annType}/{numAnnToScrap}").mkdir(parents=True, exist_ok=True)

first_try = True

# We start to scrap
for loop in tqdm(range(2, 1500, 2), position=1):
    pageNumber = str(loop).zfill(4)
    pageNumberNext = str(loop+1).zfill(4)

    status_code = None

    while status_code != 200:
        # We generate the URL of the file we want to download
        url = f"http://mesannuaires.pagesjaunes.fr/fsi/server?fext=.jpg&source=/pj/{annYear}/{annType}" \
              f"/{numAnnToScrap}/{annType:.1}{numAnnToScrap}{pageNumber}_0001.tif,/pj/{annYear}/{annType}" \
              f"/{numAnnToScrap}/{annType:.1}{numAnnToScrap}{pageNumberNext}_0001.tif&effects=&disposition=true" \
              f"&save=1&profile=doublepage&rect=0,0,1,1&height=2000&width=2306&type=image&"

        print(url)
        print()

        # We will save the file under this name
        saveas = Path(f"{annType}/{numAnnToScrap}/{annYear}_{annType}_001_{pageNumber}_{pageNumberNext}.jpg")

        # Streaming, so we can iterate over the response.
        r = requests.get(url, stream=True)
        status_code = r.status_code

        if status_code == 404:
            if first_try:
                annYear -= 1
                first_try = False
                continue
            else:
                quit()

        with saveas.open(mode='wb') as f:
            pbar = tqdm(unit="B", total=int(r.headers['Content-Length']), unit_scale=True, leave=False, position=2)
            for chunk in r.iter_content(chunk_size=CHUNK_SIZE):
                if chunk:  # filter out keep-alive new chunks
                    pbar.update(len(chunk))
                    f.write(chunk)

        first_try = False
