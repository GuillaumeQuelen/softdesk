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