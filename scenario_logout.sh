#!/bin/bash
API="http://127.0.0.1:8000/api"
PSEUDO="erin"
MDP="Azerty123!"

curl -s -o /dev/null -X POST "$API/users/" -H "Content-Type: application/json" \
  -d "{\"username\":\"$PSEUDO\",\"password\":\"$MDP\",\"age\":30}"

echo "--- 1. Connexion (attendu 200)"
REPONSE=$(curl -s -X POST "$API/token/" -H "Content-Type: application/json" \
  -d "{\"username\":\"$PSEUDO\",\"password\":\"$MDP\"}")
ACCESS=$(echo "$REPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['access'])")
REFRESH=$(echo "$REPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['refresh'])")
echo "Tokens reçus"

echo "--- 2. Déconnexion : le refresh part en liste noire (attendu 200)"
curl -s -w "\nCode HTTP : %{http_code}\n" -X POST "$API/token/blacklist/" \
  -H "Content-Type: application/json" -d "{\"refresh\":\"$REFRESH\"}"

echo "--- 3. Renouvellement avec le refresh révoqué (attendu 401)"
curl -s -w "\nCode HTTP : %{http_code}\n" -X POST "$API/token/refresh/" \
  -H "Content-Type: application/json" -d "{\"refresh\":\"$REFRESH\"}"

echo "--- 4. L'access reste valable jusqu'à son expiration (attendu 200)"
curl -s -o /dev/null -w "Code HTTP : %{http_code}\n" "$API/users/" \
  -H "Authorization: Bearer $ACCESS"