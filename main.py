# !/usr/bin/python
# -*- coding: utf-8 -*-

# PagesJaunes-Downloader
# William Gerald Blondel
# contact@williamblondel.fr

import gettext
import locale
import re
import sqlite3
import sys
from pathlib import Path

import requests

BASE_URL = "https://mesannuaires.pagesjaunes.fr"
PHONEBOOK_URL = {
    "PJA": f"{BASE_URL}/pj.php",
    "ANU": f"{BASE_URL}/pb.php"
}


def main():
    """Solocal phone books downloader."""

    # Initializing i18n
    current_locale, encoding = locale.getdefaultlocale()
    syslang = gettext.translation('PagesJaunesScraper', 'locale', languages=[current_locale], fallback="en")
    syslang.install()

    # Connecting to database
    conn = sqlite3.connect('file:phonebooks.sqlite', uri=True)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    department = None
    while department is None:
        choice_department = input(_("Department number: "))
        c.execute('SELECT * FROM departments WHERE number=? AND parent_number IS NULL', (choice_department,))
        department = c.fetchone()

    print(_("Chosen department: {} ({}).").format(department['name'], department['number']))
    print()

    directories = get_directories_for_department(c, department['number'])
    if not directories:
        _exit(c, _("No digital phone books are available for this department."))

    print(_("These phone books are available for this department: "))
    for loop in range(len(directories)):
        directory = directories[loop]
        print(f"{loop + 1}> {directory['dpt_name']} ({directory['dir_name']})")
    print()

    choice_directory = None
    while choice_directory not in range(1, len(directories)+1):
        choice_directory = int(input(_("Which one would you like to download? ")))

    with requests.Session() as s:
        directory = directories[choice_directory-1]

        s.headers.update({'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4501.0 Safari/537.36 Edg/92.0.891.1'})

        print(_("Fetching page names... "), end="")
        pagenames = get_page_names(s, directory['dpt_number'], directory['dir_acr'])

        if not pagenames:
            print(_("The phone book you requested doesn't exist. Solocal removes more and more PDF phone books."))
            print(_("Deleting the phone book from the local database... "), end="")
            delete_phonebook_from_db(c, directory['dpt_id'], directory['dir_id'])
            conn.commit()
            print(_("OK"))
            _exit(c, _("The phone book you requested doesn't exist. Solocal removes more and more PDF phone books."))

        print(_("OK"))

        print(_("Fetching the year of publication of the chosen phone book... "), end="")
        year = get_phonebook_year(s, directory['dpt_number'], directory['dir_acr'])
        if not year:
            _exit(c, _("Unable to fetch it. Unexpected error, try again."))
        print(year)

        print(_("Generating the links of the files to download... "), end="")
        urls = generate_urls_to_download(pagenames, year, directory)
        print(_("OK"))

        print(_("Creating folders... "), end="")
        folder = f"{directory['dir_acr']}"
        if directory['dpt_number'] != department['number']:
            folder += f"/{str(department['number']).zfill(3)}"
        folder += f"/{str(directory['dpt_number']).zfill(3)}/{year}"
        Path(folder).mkdir(parents=True, exist_ok=True)
        print(_("OK"))

        print(_("Downloading files..."))
        download_files(s, urls, folder)
        print(_("OK"))

        _exit(c)


def _exit(c: sqlite3.Cursor, msg: str = None):
    """Close the database connection and exit the program.

    :param c: An SQLite3 cursor.
    :param msg: Exit status.
    """
    c.close()
    sys.exit(msg)


def delete_phonebook_from_db(c: sqlite3.Cursor, department_id: int, directory_id: int) -> int:
    """Delete a phone book from the local SQLite database.

    :param c: An SQLite3 cursor.
    :param department_id: The row ID of the department in the database.
    :param directory_id: The row ID of the directory in the database.
    :return: The number of rows deleted (should be equal to 1).
    :rtype: int
    """

    c.execute("""DELETE FROM departments_directories
    WHERE department_id=? AND directory_id=?
    """, (department_id, directory_id))

    return c.rowcount


def download_files(session: requests.Session, urls: list, folder: str):
    """Downloads all the files of the phonebook.
    Doesn't download a file if it already exists.

    :param session: A Requests session.
    :param urls: The list of URLs to download.
    :param folder: The folder to which the files will be saved.
    """
    for url in urls:
        saveas = Path(f"{folder}/{Path(url.rsplit('/', 1)[-1]).stem}.jpg")
        print(saveas)

        if not saveas.exists():
            r = session.get(url, allow_redirects=True)
            if r.status_code == 200:
                with saveas.open(mode='wb') as f:
                    f.write(r.content)
            else:
                print(_("This page is missing from PagesJaunes server =/"))


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
        dir_acr = directory['dir_acr'].lower()
        dpt_number = str(directory['dpt_number']).zfill(3)
        urls.append(f"{BASE_URL}/pages/{loop+1}-large.jpg?imgpath=pj/{year}/{dir_acr}/{dpt_number}/{pagenames[loop]}")

    return urls


def get_phonebook_year(session: requests.Session, phonebook_id: int, phonebook_type: str) -> int:
    """Gets the year of publication of a specific phone book.

    :param session: A Requests session.
    :param phonebook_id: Phone book code (usually the department number).
    :param phonebook_type: Phone book type. PJA for PagesBlanches and ANU for PagesJaunes.
    :return: The year of publication of the phone book.
    :rtype: int
    """

    year = 0

    r = session.get(f"{PHONEBOOK_URL[phonebook_type]}?code={str(phonebook_id).zfill(3)}")
    r.raise_for_status()

    pattern = f"img/lib_ouv/(.*?)/{phonebook_type.lower()}/"
    substring = re.search(pattern, r.text)
    if substring:
        year = int(substring.group(1))

    return year


def get_page_names(session: requests.Session, phonebook_id: int, phonebook_type: str) -> list:
    """Gets the page names of a specific phone book.

    :param session: A Requests session.
    :param phonebook_id: Phone book code (usually the department number).
    :param phonebook_type: Phone book type. PJA for PagesBlanches and ANU for PagesJaunes.
    :return: The list of page names. Empty list if the specific phone book doesn't exist.
    :rtype: list
    """

    pagenames = []

    r = session.get(f"{PHONEBOOK_URL[phonebook_type]}?code={str(phonebook_id).zfill(3)}")
    r.raise_for_status()

    pattern = "var pagenames = \'(.*?)\'"
    substring = re.search(pattern, r.text)
    if substring and substring.group(1):
        pagenames = substring.group(1).split(',')

    return pagenames


def get_directories_for_department(c: sqlite3.Cursor, department: int) -> list:
    """Gets the list of directories for a department.

    :param c: An SQLite3 cursor.
    :param department: The department number.
    :return: The list of directories. Empty list if there is no directory for this department.
    :rtype: list
    """

    c.execute("""
    SELECT dpt.id as dpt_id, dpt.name as dpt_name, dpt.number as dpt_number,
    dir.id as dir_id, dir.name as dir_name, dir.acronyme as dir_acr
    FROM
    (
        SELECT id, name, number
        FROM departments
        WHERE number=?
        UNION
        SELECT id, name, number
        FROM departments
        WHERE parent_number=?
    ) dpt
    JOIN departments_directories dd ON dd.department_id = dpt.id
    JOIN directories dir ON dd.directory_id = dir.id
    """, (department, department))

    return c.fetchall()


if __name__ == "__main__":
    main()
