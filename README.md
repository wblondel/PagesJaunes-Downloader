# PagesJaunesScrap

Translation: [ENGLISH](README.en.md)

PagesJaunesScrap est un outil pour récupérer les annuaires Pages Jaunes
et Pages Blanches en format numérique.

L'outil télécharge les images au format JPG de l'annuaire choisi.

## Pré-requis

- Python 3.8
- requests
- lxml

En étant dans le répertoire du projet, installez les dépendances avec [Pipenv](https://pipenv.pypa.io/en/stable/install/#pragmatic-installation-of-pipenv):
```
pipenv sync
pipenv clean
```

## Avertissement

Les annuaires papier ayant perdu leur pertinence avec l'accès généralisé à Internet, la diffusion de ceux-ci est progressivement arrêtée. 2019 est la dernière édition des Pages Blanches, 2020 est la dernière édition des Pages Jaunes. Certains départements n'ont pas eu d'édition récente, et les anciennes éditions ne sont pas disponibles sur le catalogue. De ce fait, de plus en plus d'annuaires numérisés sont/deviennent indisponibles sur le catalogue en ligne, au profit du site [PagesJaunes](https://www.pagesjaunes.fr/).

L'outil vous propose les annuaires disponibles pour le département que vous avez choisi en consultant une base de données que j'ai constituée (phonebooks.sqlite), mais il se peut que certains annuaires soient devenus indisponibles entre temps.

## Des questions, des commentaires, etc?

Vous pouvez me contacter, créer un ticket ou un pull request.

GitHub: https://github.com/wblondel <br/> Twitter:
http://twitter.com/wgblondel <br/> Email: contact@williamblondel.fr
