# SoftDesk Support

API RESTful de suivi de problèmes techniques, développée avec Django REST Framework.
Les utilisateurs créent des projets, y invitent des contributeurs, signalent des
issues (bugs, fonctionnalités, tâches) et les commentent.

## Installation

Prérequis : Python 3.12 et Pipenv.

```bash
git clone https://github.com/GuillaumeQuelen/softdesk.git
cd softdesk
pipenv install
cp .env.example .env
```

Générer une clé secrète et la coller dans `.env`, entre apostrophes :

```bash
pipenv run python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Puis créer la base :

```bash
pipenv run python manage.py migrate
```

## Lancement

```bash
pipenv run python manage.py runserver
```

L'API est disponible sur `http://127.0.0.1:8000/api/`.

## Authentification

L'API utilise des jetons JWT. On obtient un jeton en envoyant son pseudo et son mot de passe
à `POST /api/token/`, puis on l'ajoute à chaque requête dans l'en-tête
`Authorization: Bearer <access>`. Le jeton d'accès expire après 5 minutes ;
`POST /api/token/refresh/` en fournit un nouveau à partir du jeton de rafraîchissement (1 jour).

## Points de terminaison

| Adresse | Méthodes | Qui peut |
|---|---|---|
| `/api/users/` | POST | tout le monde (inscription) |
| `/api/users/` et `/api/users/{id}/` | GET, PUT, PATCH, DELETE | l'utilisateur, sur son propre compte uniquement |
| `/api/projects/` | GET, POST | utilisateur connecté (ne voit que ses projets) |
| `/api/projects/{id}/` | GET | contributeurs |
| `/api/projects/{id}/` | PUT, PATCH, DELETE | auteur du projet |
| `/api/projects/{id}/contributors/` | GET | contributeurs |
| `/api/projects/{id}/contributors/` | POST | auteur du projet |
| `/api/projects/{id}/contributors/{id}/` | DELETE | auteur du projet |
| `/api/projects/{id}/issues/` | GET, POST | contributeurs |
| `/api/projects/{id}/issues/{id}/` | PUT, PATCH, DELETE | auteur de l'issue |
| `/api/projects/{id}/issues/{id}/comments/` | GET, POST | contributeurs |
| `/api/projects/{id}/issues/{id}/comments/{id}/` | PUT, PATCH, DELETE | auteur du commentaire |
| `/api/token/blacklist/` | POST | Se déconnecter : révoque le refresh token (envoyé dans le corps) |

Les listes sont paginées par 10 (`?limit=` et `?offset=` pour naviguer).

## Choix de conception

- **Ajout d'un contributeur par pseudo.** Un utilisateur ne voit que son propre compte.
  L'auteur d'un projet ajoute donc un contributeur en indiquant son pseudo
  (`{"username": "bob"}`), que les membres d'une équipe s'échangent entre eux.
- **L'auteur d'un projet en devient automatiquement contributeur.**
- **Une issue ne peut être assignée qu'à un contributeur du projet.**
- **Cacher plutôt qu'interdire.** Une ressource d'un projet dont on n'est pas contributeur
  renvoie `404`, pour ne pas révéler son existence. Une action interdite sur une ressource
  visible renvoie `403`.

## Sécurité et RGPD

- **Âge minimal** : l'inscription est refusée en dessous de 15 ans.
- **Consentements** : `can_be_contacted` et `can_data_be_shared` sont désactivés par défaut.
- **Mots de passe** : hachés par Django (PBKDF2), jamais renvoyés par l'API.
- **Droit à l'oubli** : la suppression d'un compte supprime ses projets. Ses issues et
  commentaires sont conservés sans auteur, pour que les autres contributeurs ne perdent
  ni le suivi des bugs ni leurs propres commentaires.
- **Contrôle d'accès (OWASP A01)** : filtrage des données visibles et permission réservée
  à l'auteur pour les modifications.
- **Configuration (OWASP A05)** : `DEBUG` désactivé et clé secrète hors du code, dans `.env`.
- **Authentification (OWASP A07)** : jeton d'accès de courte durée.
- **Dépendances (OWASP A06)** : versions figées dans `Pipfile.lock`.
- Mots de passe vérifiés par les validateurs de Django, puis hachés (PBKDF2)
- Déconnexion : liste noire des refresh tokens, avec rotation
- Limitation des requêtes : 30 par minute sans token, 300 connecté (429 au-delà)
- Green code : `select_related` sur les issues et commentaires

## Tests

### Tests automatisés (sans serveur)

    pipenv run python manage.py test

- `users/tests.py` : règle des 15 ans, déconnexion (refresh refusé après révocation)
- `projects/tests.py` : assignation, permissions (403, 404), pagination, nombre de requêtes constant

### Scénarios de démonstration (serveur lancé)

    ./scenario_issues.sh     # les 12 étapes du cahier des charges
    ./scenario_logout.sh     # connexion, déconnexion, refresh refusé
```
Vérifier la qualité du code :

```bash
pipenv install --dev
pipenv run flake8
```