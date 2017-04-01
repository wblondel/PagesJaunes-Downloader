# !/usr/bin/python
# -*- coding: utf-8 -*-

# PagesJaunesScrap Copyright (C) 2017    William Gerald Blondel
# contact@williamblondel.fr
# Last modified 2nd April 2017 12.33am

# TODO : Reformat the print()
# TODO : Give the choice between PagesJaunes and PagesBlanches

import json
from pathlib import Path
from tqdm import tqdm
import requests


DIRECTORIES_LIST_FILENAME = Path("liste_annuaires.json")
CHUNK_SIZE = 1024

# We load the list of directories
with DIRECTORIES_LIST_FILENAME.open() as directories_list_fileobject:
    directories = json.load(directories_list_fileobject)

directories = directories["annuaires"]

# We ask the user which directory he wants to scrap
numAnnToScrap = None
annType = None
annYear = 2017

while numAnnToScrap not in [item["numAnn"] for item in directories]:
    numAnnToScrap = input("Veuillez entrer le numéro du département dont vous voulez récupérer l'annuaire : ").zfill(3)

dptToScrap = [item for item in directories if item['numAnn'] == numAnnToScrap][0]
print("Vous avez choisi le département {} ({}).".format(dptToScrap["nomDpt"], dptToScrap["numAnn"]))
print()

if len(dptToScrap) > 2:
    print("Ce département a plusieurs annuaires.")

    for subAnn in dptToScrap["sousAnn"]:
        print("> {} ({})".format(subAnn["nomAnn"], subAnn["numAnn"]))

    while numAnnToScrap not in [item["numAnn"] for item in dptToScrap["sousAnn"]]:
        numAnnToScrap = input("Lequel voulez-vous récupérer ? ")

    print()
    print("Vous avez choisi l'annuaire {}.".format(numAnnToScrap))
    print()

while annType not in ["pja", "anu"]:
    annType = input("Voulez-vous récupérer l'annuaire PagesJaunes (PJA) ou PagesBlanches (ANU) ? ").lower()

# We create the folder where the files will be downloaded
Path("{}/{}".format(annType, numAnnToScrap)).mkdir(parents=True, exist_ok=True)

first_try = True

# We start to scrap
for loop in tqdm(range(2, 1500, 2), position=1):
    pageNumber = str(loop).zfill(4)
    pageNumberNext = str(loop+1).zfill(4)

    status_code = None

    while status_code != 200:
        # We generate the URL of the file we want to download
        # {0} = annYear
        # {1} = annType
        # {2} = numAnnToScrap
        # {3} = pageNumber
        # {4} = pageNumberNext
        url = "http://mesannuaires.pagesjaunes.fr/fsi/server?" \
              "fext=.jpg&" \
              "source=/pj/{0}/{1}/{2}/{1:.1}{2}{3}_0001.tif,/pj/{0}/{1}/{2}/{1:.1}{2}{4}_0001.tif&" \
              "effects=&" \
              "disposition=true&" \
              "save=1&" \
              "profile=doublepage&" \
              "rect=0,0,1,1&" \
              "height=2000&" \
              "width=2306&" \
              "type=image&"\
            .format(annYear, annType, numAnnToScrap, pageNumber, pageNumberNext)

        # We will save the file under this name
        saveas = Path("{0}/{1}/{2}_PJ_001_{3}_{4}.jpg"
                      .format(annType, numAnnToScrap, annYear, pageNumber, pageNumberNext))

        # Streaming, so we can iterate over the response.
        r = requests.get(url, stream=True)
        status_code = r.status_code

        if status_code == 404:
            if first_try:
                annYear -= 1
                first_try = False
                break
            else:
                quit()

        with saveas.open(mode='wb') as f:
            pbar = tqdm(unit="B", total=int(r.headers['Content-Length']), unit_scale=True, leave=False, position=2)
            for chunk in r.iter_content(chunk_size=CHUNK_SIZE):
                if chunk:  # filter out keep-alive new chunks
                    pbar.update(len(chunk))
                    f.write(chunk)

        first_try = False
