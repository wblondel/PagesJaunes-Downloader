# !/usr/bin/python
# -*- coding: utf-8 -*-

# PagesJaunesScrap
# William Gerald Blondel
# contact@williamblondel.fr

import gettext
import requests
import sqlite3
import re
from pathlib import Path

BASE_URL = "https://mesannuaires.pagesjaunes.fr"
PHONEBOOK_URL = {
    "PJA": f"{BASE_URL}/pj.php",
    "ANU": f"{BASE_URL}/pb.php"
}


def main():
    """Solocal phone books downloader."""

    localedir = "./locale"
    translate = gettext.translation('PagesJaunesScraper', localedir, fallback=True)
    _ = translate.gettext

    conn = sqlite3.connect('file:phonebooks.sqlite?mode=ro', uri=True)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    department = None
    while department is None:
        departmentnumber = input(_("Veuillez entrer le numéro du département dont vous voulez récupérer l'annuaire : "))
        c.execute('SELECT * FROM departments WHERE number=?', (departmentnumber,))
        department = c.fetchone()

    print(_(f"Vous avez choisi le département {department['name']} ({department['number']})."))
    print()

    directories = get_directories_for_department(c, department['number'])
    if not directories:
        exit(_("Aucun annuaire numérisé n'est disponible pour ce département."))

    print(_("Les annuaires disponibles sont : "))
    for loop in range(len(directories)):
        directory = directories[loop]
        print(f"{loop + 1}> {directory['name']} ({directory['dirname']})")
    print()

    dir_index = None
    while dir_index not in range(1, len(directories)+1):
        dir_index = int(input(_("Lequel voulez-vous récupérer ? ")))

    with requests.Session() as s:
        directory = directories[dir_index-1]

        print(_("Récupération du nom des pages... "), end="")
        pagenames = get_page_names(s, str(directory['number']), directory['diracr'])
        if not pagenames:
            exit(_("The phone book you requested doesn't exist. Solocal removes more and more PDF phone books."))
        print(_("OK"))

        print(_("Récupération de l'année de publication de l'annuaire... "), end="")
        year = get_phonebook_year(s, str(directory['number']), directory['diracr'])
        if not year:
            exit(_("Can't get the year of publication of this phone book (unexpected error, try again.)"))
        print(year)

        print(_("Génération des URL des fichiers à télécharger... "), end="")
        urls = generate_urls_to_download(pagenames, year, directory)
        print(_("OK"))

        print(_("Création des dossiers... "), end="")
        folder = f"{directory['diracr']}"
        if directory['number'] != department['number']:
            folder += f"/{str(department['number']).zfill(3)}"
        folder += f"/{str(directory['number']).zfill(3)}/{year}"
        Path(folder).mkdir(parents=True, exist_ok=True)
        print(_("OK"))

        print(_("Téléchargement des fichiers..."))
        download_files(s, urls, folder)
        print(_("OK"))


def download_files(session: requests.Session, urls: list, folder: str):
    """Downloads all the files of the phonebook.

    :param session: Our Requests session.
    :param urls: The list of URLs to download.
    :param folder: The folder to which the files will be saved.
    """
    for url in urls:
        saveas = Path(f"{folder}/{Path(url.rsplit('/', 1)[-1]).stem}.jpg")
        print(saveas)
        r = session.get(url, allow_redirects=True)
        r.raise_for_status()
        with saveas.open(mode='wb') as f:
            f.write(r.content)


def generate_urls_to_download(pagenames: list, year: int, directory: sqlite3.Row) -> list:
    """Generates the list of URLs to download.

    :param pagenames: List of page names
    :param year: The year of publication of the phonne book
    :param directory: A directory row
    :return: The list of URLs to download
    :rtype: list
    """

    urls = []

    for loop in range(len(pagenames)):
        dir_acr = directory['diracr'].lower()
        dir_number = str(directory['number']).zfill(3)
        urls.append(f"{BASE_URL}/pages/{loop+1}-large.jpg?imgpath=pj/{year}/{dir_acr}/{dir_number}/{pagenames[loop]}")

    return urls


def get_phonebook_year(session: requests.Session, phonebook_id: str, phonebook_type: str) -> int:
    """Gets the year of publication of a specific phone book.

    :param session: Our Requests session.
    :param phonebook_id: Phone book code (usually the department number).
    :param phonebook_type: Phone book type. PJA for PagesBlanches and ANU for PagesJaunes.
    :return: The year of publication of the phone book.
    :rtype: int
    """

    year = 0

    r = session.get(f"{PHONEBOOK_URL[phonebook_type]}?code={phonebook_id.zfill(3)}")
    r.raise_for_status()

    pattern = f"img/lib_ouv/(.*?)/{phonebook_type.lower()}/"
    substring = re.search(pattern, r.text)
    if substring:
        year = int(substring.group(1))

    return year


def get_page_names(session: requests.Session, phonebook_id: str, phonebook_type: str) -> list:
    """Gets the page names of a specific phone book.

    :param session: Our Requests session.
    :param phonebook_id: Phone book code (usually the department number).
    :param phonebook_type: Phone book type. PJA for PagesBlanches and ANU for PagesJaunes.
    :return: The list of page names. Empty list if the specific phone book doesn't exist.
    :rtype: list
    """

    pagenames = []

    r = session.get(f"{PHONEBOOK_URL[phonebook_type]}?code={phonebook_id.zfill(3)}")
    r.raise_for_status()

    pattern = "var pagenames = \'(.*?)\'"
    substring = re.search(pattern, r.text)
    if substring and substring.group(1):
        pagenames = substring.group(1).split(',')

    return pagenames


def get_directories_for_department(c: sqlite3.Cursor, department: int) -> list:
    """Gets the list of directories for a department.

    :param c: Our SQLite3 cursor.
    :param department: The department number.
    :return: The list of directories. Empty list if there is no directory for this department.
    :rtype: list
    """

    c.execute("""
    SELECT t1.id, t1.name, t1.number, directories.name as dirname, directories.acronyme as diracr
    FROM
    (
        SELECT id, name, number
        FROM departments
        WHERE number=?
        UNION
        SELECT id, name, number
        FROM departments
        WHERE parent_number=?
    ) t1
    JOIN departments_directories ON departments_directories.department_id = t1.id
    JOIN directories ON departments_directories.directory_id = directories.id
    """, (department, department))

    return c.fetchall()


if __name__ == "__main__":
    main()
