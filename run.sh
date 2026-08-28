#!/bin/sh
set -e

root=$(CDPATH= cd -- "$(dirname "$0")" && pwd)
cd "$root"

if [ ! -f backend/.env ]; then
  cp backend/.env.example backend/.env
fi

docker compose -f backend/docker-compose.yml up --build -d

echo "Aguardando a API em http://localhost:8000 ..."
i=0
while [ "$i" -lt 60 ]; do
  if docker compose -f backend/docker-compose.yml exec -T web \
    python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/admin/login/')" \
    >/dev/null 2>&1; then
    break
  fi
  i=$((i + 1))
  sleep 1
done
if [ "$i" -eq 60 ]; then
  echo "A API não respondeu. Logs: docker compose -f backend/docker-compose.yml logs web" >&2
  exit 1
fi

cd frontend
if [ ! -d node_modules ]; then
  # --userconfig aponta para o .npmrc do projeto para o ~/.npmrc da máquina não
  # redirecionar o install para outro registry.
  npm install --userconfig ./.npmrc --registry https://registry.npmjs.org/
fi

echo "App: http://localhost:3000  (atendente / 123)"
echo "API: http://localhost:8000  Admin: http://localhost:8000/admin/"
exec npm run dev
