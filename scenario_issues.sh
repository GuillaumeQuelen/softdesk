#!/bin/bash
# Scénario de test des issues. À lancer avec le serveur démarré.
API=http://127.0.0.1:8000/api

token() {
  curl -sS -X POST "$API/token/" -H "Content-Type: application/json" \
    -d "{\"username\":\"$1\",\"password\":\"$2\"}" \
    | python3 -c "import sys, json; print(json.load(sys.stdin)['access'])"
}

appel() {
  # $1 = description, $2 = méthode, $3 = token, $4 = adresse, $5 = données JSON
  echo "--- $1"
  curl -sS -w "\nCode HTTP : %{http_code}\n\n" -X "$2" "$API$4" \
    -H "Authorization: Bearer $3" -H "Content-Type: application/json" \
    -d "$5"
}

CAROL=$(token carol 'NouveauMdp456!')
BOB=$(token bob 'Azerty123!')

appel "1. carol crée une issue assignée à bob (attendu 201)" POST "$CAROL" /projects/1/issues/ \
  '{"title":"Bug login","description":"Erreur 500","priority":"HIGH","tag":"BUG","assigned_to":"bob"}'

appel "2. assignée à alice, qui n'existe pas (attendu 400)" POST "$CAROL" /projects/1/issues/ \
  '{"title":"Test","description":"x","priority":"LOW","tag":"TASK","assigned_to":"alice"}'

appel "3. assignée à dave, non contributeur (attendu 400)" POST "$CAROL" /projects/1/issues/ \
  '{"title":"Test","description":"x","priority":"LOW","tag":"TASK","assigned_to":"dave"}'

appel "4. bob crée sa propre issue (attendu 201)" POST "$BOB" /projects/1/issues/ \
  '{"title":"Feature export","description":"CSV","priority":"MEDIUM","tag":"FEATURE"}'

appel "5. bob modifie l'issue de carol (attendu 403)" PATCH "$BOB" /projects/1/issues/1/ \
  '{"status":"FINISHED"}'

DAVE=$(token dave 'Azerty123!')

appel "6. carol commente l'issue 1 (attendu 201)" POST "$CAROL" /projects/1/issues/1/comments/ \
  '{"description":"Je regarde ça demain."}'

appel "7. bob, contributeur, commente aussi (attendu 201)" POST "$BOB" /projects/1/issues/1/comments/ \
  '{"description":"Je peux aider."}'

appel "8. dave, non contributeur, tente de commenter (attendu 404)" POST "$DAVE" /projects/1/issues/1/comments/ \
  '{"description":"Intrusion"}'

appel "9. bob modifie le commentaire de carol (attendu 403)" PATCH "$BOB" /projects/1/issues/1/comments/1/ \
  '{"description":"Modifié par bob"}'