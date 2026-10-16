#!/bin/bash
# Scénario de test complet de l'API SoftDesk. À lancer avec le serveur démarré.
API=http://127.0.0.1:8000/api

if ! curl -s -o /dev/null "$API/"; then
  echo "Le serveur ne répond pas : lancez d'abord 'pipenv run python manage.py runserver'."
  exit 1
fi

inscrire() {
  # Crée l'utilisateur s'il n'existe pas encore (sinon l'API répond 400, sans conséquence)
  curl -sS -o /dev/null -X POST "$API/users/" -H "Content-Type: application/json" \
    -d "{\"username\":\"$1\",\"password\":\"$2\",\"age\":$3}"
}

token() {
  curl -sS -X POST "$API/token/" -H "Content-Type: application/json" \
    -d "{\"username\":\"$1\",\"password\":\"$2\"}" \
    | python3 -c "import sys, json; print(json.load(sys.stdin)['access'])"
}

id_de() {
  python3 -c "import sys, json; print(json.load(sys.stdin)['id'])"
}

appel() {
  # $1 = description, $2 = méthode, $3 = token, $4 = adresse, $5 = données JSON
  echo "--- $1"
  REPONSE=$(curl -sS -w "\n%{http_code}" -X "$2" "$API$4" \
    -H "Authorization: Bearer $3" -H "Content-Type: application/json" -d "$5")
  CORPS=$(echo "$REPONSE" | sed '$d')
  echo "$CORPS"
  echo "Code HTTP : $(echo "$REPONSE" | tail -n 1)"
  echo
}

echo "=== Préparation des données"
inscrire carol 'Azerty123!' 25
inscrire bob 'Azerty123!' 30
inscrire dave 'Azerty123!' 40
CAROL=$(token carol 'Azerty123!')
BOB=$(token bob 'Azerty123!')
DAVE=$(token dave 'Azerty123!')

PROJET=$(curl -sS -X POST "$API/projects/" -H "Authorization: Bearer $CAROL" \
  -H "Content-Type: application/json" \
  -d '{"title":"Site vitrine","description":"Refonte","type":"FRONTEND"}' | id_de)
curl -sS -o /dev/null -X POST "$API/projects/$PROJET/contributors/" \
  -H "Authorization: Bearer $CAROL" -H "Content-Type: application/json" \
  -d '{"username":"bob"}'
echo "Projet $PROJET créé par carol, bob ajouté comme contributeur, dave n'en fait pas partie"
echo

echo "=== Scénario"
echo "--- 0. alice, 12 ans, tente de s'inscrire (attendu 400)"
curl -sS -w "\nCode HTTP : %{http_code}\n\n" -X POST "$API/users/" \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"Azerty123!","age":12}'

appel "1. carol crée une issue assignée à bob (attendu 201)" POST "$CAROL" "/projects/$PROJET/issues/" \
  '{"title":"Bug login","description":"Erreur 500","priority":"HIGH","tag":"BUG","assigned_to":"bob"}'
ISSUE=$(echo "$CORPS" | id_de)

appel "2. assignée à alice, qui n'existe pas (attendu 400)" POST "$CAROL" "/projects/$PROJET/issues/" \
  '{"title":"Test","description":"x","priority":"LOW","tag":"TASK","assigned_to":"alice"}'

appel "3. assignée à dave, non contributeur (attendu 400)" POST "$CAROL" "/projects/$PROJET/issues/" \
  '{"title":"Test","description":"x","priority":"LOW","tag":"TASK","assigned_to":"dave"}'

appel "4. bob crée sa propre issue (attendu 201)" POST "$BOB" "/projects/$PROJET/issues/" \
  '{"title":"Feature export","description":"CSV","priority":"MEDIUM","tag":"FEATURE"}'

appel "5. bob modifie l'issue de carol (attendu 403)" PATCH "$BOB" "/projects/$PROJET/issues/$ISSUE/" \
  '{"status":"FINISHED"}'

appel "6. carol commente son issue (attendu 201)" POST "$CAROL" "/projects/$PROJET/issues/$ISSUE/comments/" \
  '{"description":"Je regarde ça demain."}'
COMMENTAIRE=$(echo "$CORPS" | id_de)

appel "7. bob, contributeur, commente aussi (attendu 201)" POST "$BOB" "/projects/$PROJET/issues/$ISSUE/comments/" \
  '{"description":"Je peux aider."}'

appel "8. dave, non contributeur, tente de commenter (attendu 404)" POST "$DAVE" "/projects/$PROJET/issues/$ISSUE/comments/" \
  '{"description":"Intrusion"}'

appel "9. bob modifie le commentaire de carol (attendu 403)" PATCH "$BOB" "/projects/$PROJET/issues/$ISSUE/comments/$COMMENTAIRE/" \
  '{"description":"Modifié par bob"}'

appel "10. bob tente de supprimer le projet de carol (attendu 403)" DELETE "$BOB" "/projects/$PROJET/" ''

appel "11. carol liste les issues du projet, paginées (attendu 200)" GET "$CAROL" "/projects/$PROJET/issues/" ''