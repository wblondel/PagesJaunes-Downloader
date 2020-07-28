# PagesJaunesScrap

Translation: [FRENCH](README.md)

PagesJaunesScrap is a tool to download the digital editions of the French phone books: PagesJaunes and PagesBlanches.

The tool downloads the chosen phonebook in JPG format.

## Dependencies

- Python 3.8
- requests

Move to the project directory and install the dependencies with [Pipenv](https://pipenv.pypa.io/en/stable/install/#pragmatic-installation-of-pipenv):
```
pipenv sync
pipenv clean
```

## Disclaimer

The advent of the Internet and smartphones greatly reduced the need for a paper phone book. 2019 is the last edition of Pages Blanches, 2020 is the last edition of Pages Jaunes. Some departments didn't get a recent edition, and only the latest edition is available online. Therefore, more and more digital phone books can't be downloaded anymore, for the benefit of the [PagesJaunes](https://www.pagesjaunes.fr/) website.

When selecting a department, the tool shows which phone books are available by checking a database I created (phonebooks.sqlite). However, a phone book you selected may have been deleted since the latest update of this database. The program will update the local database so that it doesn't list this phone book anymore.

## An issue? A comment? An idea?

You can contact me, create a ticket or a pull request.

GitHub: https://github.com/wblondel <br/> Twitter:
http://twitter.com/wgblondel <br/> Email: contact@williamblondel.fr
