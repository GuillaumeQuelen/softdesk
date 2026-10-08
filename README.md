# SoftDesk Support

API RESTful de suivi de tickets techniques (projets, contributeurs, issues, commentaires), construite avec Django REST Framework.

## Prérequis

- Python 3.12
- Pipenv

## Installation

```bash
git clone https://github.com/GuillaumeQuelen/softdesk.git
cd softdesk
pipenv install
pipenv shell
```

## Lancement

```bash
python manage.py migrate
python manage.py runserver
```

L'API est alors disponible sur http://127.0.0.1:8000/


## Cas d'utilisation principal
---
Un développeur crée un projet (back-end, front-end, iOS ou Android).
Il invite d'autres développeurs à y contribuer (POST /contributors/).
Les contributeurs voient le projet et peuvent créer des issues 
(bugs, features, tasks) et y laisser des commentaires.
L'auteur du projet contrôle qui peut contribuer (ajouter/retirer 
des contributeurs). Seul l'auteur d'une issue peut la réassigner.

## Données sensibles
---
- Identifiants et emails des utilisateurs
- Contenu des issues et commentaires (peut contenir du code)
- Métadonnées de timing (qui fait quoi, quand)

## Risques OWASP
---
- A01 : un développeur voit les issues d'un projet où il n'est
  pas contributeur
- A04 : les utilisateurs doivent avoir 15 ans (conception RGPD)
- A05 : les erreurs de l'API exposent la configuration (DEBUG = True)
- A07 : les tokens JWT de longue durée peuvent être volés