# !/usr/bin/python
# -*- coding: utf-8 -*-

# PagesJaunesScrap Copyright (C) 2017    William Gerald Blondel
# contact@williamblondel.fr
# Last modified 31st April 2017 11.29pm

import json

DIRECTORIES_LIST_FILENAME = "liste_annuaires.json"

# We load the list of directories
with open(DIRECTORIES_LIST_FILENAME) as directories_list_fileobject:
    directories = json.load(directories_list_fileobject)

directories = directories["annuaires"]

