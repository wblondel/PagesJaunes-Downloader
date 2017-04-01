# !/usr/bin/python
# -*- coding: utf-8 -*-

# PagesJaunesScrap Copyright (C) 2017    William Gerald Blondel
# contact@williamblondel.fr
# Last modified 31st April 2017 11.29pm

# TODO : Reformat the print()

import json

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

