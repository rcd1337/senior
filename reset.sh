#!/bin/sh
set -e

root=$(CDPATH= cd -- "$(dirname "$0")" && pwd)
cd "$root"

if [ ! -f backend/.env ]; then
  cp backend/.env.example backend/.env
fi

compose="docker compose -f backend/docker-compose.yml"

# -v apaga o volume do Postgres; o entrypoint refaz migrate + seed no próximo up.
$compose down -v
$compose up --build -d

echo "Aguardando a API em http://localhost:8000 ..."
i=0
while [ "$i" -lt 60 ]; do
  if $compose exec -T web \
    python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/admin/login/')" \
    >/dev/null 2>&1; then
    break
  fi
  i=$((i + 1))
  sleep 1
done
if [ "$i" -eq 60 ]; then
  echo "A API não respondeu. Logs: $compose logs web" >&2
  exit 1
fi

echo "Banco recriado com o seed."
echo "App: http://localhost:3000  (atendente / 123)"
echo "API: http://localhost:8000  Docs: http://localhost:8000/api/docs/  Admin: http://localhost:8000/admin/"
