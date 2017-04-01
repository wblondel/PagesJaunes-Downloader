# !/usr/bin/python
# -*- coding: utf-8 -*-

# PagesJaunesScrap Copyright (C) 2017    William Gerald Blondel
# contact@williamblondel.fr
# Last modified 31st April 2017 11.29pm

# TODO : Reformat the print()
# TODO : Give the choice between PagesJaunes and PagesBlanches

import json
from tqdm import tqdm
import requests


DIRECTORIES_LIST_FILENAME = "liste_annuaires.json"

# We load the list of directories
with open(DIRECTORIES_LIST_FILENAME) as directories_list_fileobject:
    directories = json.load(directories_list_fileobject)

directories = directories["annuaires"]

# We ask the user which directory he wants to scrap
numAnnToScrap = 0

while numAnnToScrap not in [item["numAnn"] for item in directories]:
    numAnnToScrap = input("Veuillez entrer le numéro du département dont vous voulez récupérer l'annuaire : ").zfill(3)

dptToScrap = [item for item in directories if item['numAnn'] == numAnnToScrap][0]
print("Vous avez choisi le département " + dptToScrap['nomDpt'] + " (" + dptToScrap['numAnn'] + ").")
print()

if len(dptToScrap) > 2:
    print("Ce département a plusieurs annuaires.")

    for subAnn in dptToScrap["sousAnn"]:
        print("> ", subAnn['nomAnn'] + " (" + subAnn['numAnn'] + ")")

    while numAnnToScrap not in [item["numAnn"] for item in dptToScrap["sousAnn"]]:
        numAnnToScrap = input("Lequel voulez-vous récupérer ? ")

    print()
    print("Vous avez choisi l'annuaire", numAnnToScrap + ".")

# We start to scrap
for loop in tqdm(range(2, 700, 2), position=1):
    pageNumber = str(loop).zfill(4)
    pageNumberNext = str(loop+1).zfill(4)

    url = "http://mesannuaires.pagesjaunes.fr/fsi/server?fext=%2Ejpg&source=%2Fpj%2F2016%2Fpja%2F" + numAnnToScrap + "%2Fp" + numAnnToScrap + pageNumber + "%5F0001%2Etif,%2Fpj%2F2016%2Fpja%2F" + numAnnToScrap + "%2Fp" + numAnnToScrap + pageNumberNext + "%5F0001%2Etif&effects=&disposition=true&save=1&profile=doublepage&rect=0%2C0%2C1%2C1&height=2000&width=2306&type=image&savename=2016%5FPJ%5F001%5F350%5F351"
    saveas = numAnnToScrap + "/" + "2016_PJ_001_" + pageNumber + "_" + pageNumberNext + ".jpg"

    # Streaming, so we can iterate over the response.
    r = requests.get(url, stream=True)

    if r.status_code == 404:
        break

    chunkSize = 1024

    with open(saveas, 'wb') as f:
        pbar = tqdm(unit="B", total=int(r.headers['Content-Length']), unit_scale=True, leave=False, position=2)
        for chunk in r.iter_content(chunk_size=chunkSize):
            if chunk: # filter out keep-alive new chunks
                pbar.update (len(chunk))
                f.write(chunk)
