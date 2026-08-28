# Hotel — gestão de hóspedes

Django + DRF + PostgreSQL e React (Vite). Recepção: hóspedes, reservas, check-in, check-out e conta.

## Tecnologias

- Python 3.12 e Django 5.2 (LTS)
- Django REST framework
- PostgreSQL 16
- Docker
- JWT
- Node.js, npm e React 19 (Vite)

## Pré-requisitos

- Docker e Docker Compose
- Node.js 18+ e npm

## Inicialização

Clone o repositório:

```bash
git clone https://github.com/rcd1337/senior.git
cd senior
```

### Opção 1 - "automático" (script c/ comando único)

```bash
chmod +x run.sh
./run.sh
```

Sobe o Postgres e a API em background, espera o migrate/seed, instala o front se precisar e abre o Vite. Ctrl+C para o React; a API continua no Docker.

```bash
docker compose -f backend/docker-compose.yml down
```

Browser: [http://localhost:3000](http://localhost:3000) — `atendente` / `123`.

### Opção 2 - manual (2 terminais, back e front)

1. Copie o env (só na primeira vez):

   ```bash
   cp backend/.env.example backend/.env
   ```

2. Suba a API e o banco:

   ```bash
   cd backend
   docker compose up --build
   ```

   Espere o `runserver`. O container aplica as migrations e o seed sozinho. API: [http://localhost:8000](http://localhost:8000). Admin: [http://localhost:8000/admin/](http://localhost:8000/admin/).

3. Em **outro** terminal, o React:

   ```bash
   cd frontend
   npm install --userconfig ./.npmrc --registry https://registry.npmjs.org/
   npm run dev
   ```

4. Abra [http://localhost:3000](http://localhost:3000) e entre com `atendente` / `123`.

### Contas (senha `123`)

O campo de login aceita **username ou e-mail**.

| Papel | Username | E-mail | Onde |
|---|---|---|---|
| Atendente | `atendente` | `atendente@exemplo.com` | app |
| Superuser | `superuser` | `superuser@exemplo.com` | Django admin |

### Seed

| Hóspede | Situação |
|---|---|
| Frank Reynolds | Hospedado, **com** carro |
| Charlie Kelly | Hospedado, **sem** carro |
| Ronald "Mac" McDonald | Reservado (pendente de check-in) |
| Dennis Reynolds, Dee Reynolds | Só ficha, sem reserva |

## API

Prefixo: `/api/v1/`. Rotas autenticadas (exceto o token) exigem `Authorization: Bearer <access>`.

- `POST /auth/token/` — `{ "login", "password" }`
- `POST /auth/token/refresh/` — `{ "refresh" }`
- `GET /guests/?search=` — nome, documento ou telefone
- `GET /guests/?status=` — `reserved` \| `checked_in` \| `checked_out`
- `POST /guests/`
- `GET /reservations/`
- `POST /reservations/`
- `POST /reservations/{id}/check-in/`
- `POST /reservations/{id}/check-out/`

## Regras de preço

| Item | Dia útil | Fim de semana |
|---|---|---|
| Diária | R$ 120 | R$ 180 |
| Vaga | R$ 15 | R$ 20 |

Check-in a partir das 14h: se for antes, o sistema **registra** e devolve um alerta (não bloqueia).

Check-out até 12h: depois disso, +50% da **diária daquele dia**. A conta detalhada vem no check-out.

## Testes

Com a stack do Docker já buildada:

```bash
docker compose -f backend/docker-compose.yml run --rm --no-deps web pytest
```

```bash
cd frontend
npm test
```

O `pytest` nesse comando usa SQLite (`--no-deps` não sobe o Postgres). O `docker compose up` continua no PostgreSQL.
