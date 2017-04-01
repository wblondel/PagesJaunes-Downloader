# !/usr/bin/python
# -*- coding: utf-8 -*-

# PagesJaunesScrap Copyright (C) 2017    William Gerald Blondel
# contact@williamblondel.fr
# Last modified 1st April 2017 05.24pm

# TODO : Reformat the print()
# TODO : Give the choice between PagesJaunes and PagesBlanches

import json
from pathlib import Path
from tqdm import tqdm
import requests


DIRECTORIES_LIST_FILENAME = Path("liste_annuaires.json")

# We load the list of directories
with DIRECTORIES_LIST_FILENAME.open() as directories_list_fileobject:
    directories = json.load(directories_list_fileobject)

directories = directories["annuaires"]

# We ask the user which directory he wants to scrap
numAnnToScrap = 0

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

# We create the folder where the files will be downloaded
Path(numAnnToScrap).mkdir(exist_ok=True)

# We start to scrap
for loop in tqdm(range(2, 700, 2), position=1):
    pageNumber = str(loop).zfill(4)
    pageNumberNext = str(loop+1).zfill(4)

    # {0} = numAnnToScrap
    # {1} = pageNumber
    # {2} = pageNumberNext
    url = "http://mesannuaires.pagesjaunes.fr/fsi/server?" \
          "fext=.jpg&" \
          "source=/pj/2016/pja/{0}/p{0}{1}_0001.tif,/pj/2016/pja/{0}/p{0}{2}_0001.tif&" \
          "effects=&" \
          "disposition=true&" \
          "save=1&" \
          "profile=doublepage&" \
          "rect=0,0,1,1&" \
          "height=2000&" \
          "width=2306&" \
          "type=image&" \
        .format(numAnnToScrap, pageNumber, pageNumberNext)

    saveas = Path("{0}/2016_PJ_001_{1}_{2}.jpg".format(numAnnToScrap, pageNumber, pageNumberNext))

    # Streaming, so we can iterate over the response.
    r = requests.get(url, stream=True)

    if r.status_code == 404:
        break

    chunkSize = 1024

    with saveas.open(mode='wb') as f:
        pbar = tqdm(unit="B", total=int(r.headers['Content-Length']), unit_scale=True, leave=False, position=2)
        for chunk in r.iter_content(chunk_size=chunkSize):
            if chunk:  # filter out keep-alive new chunks
                pbar.update(len(chunk))
                f.write(chunk)
