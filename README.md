# Hotel — gestão de hóspedes

Aplicação do desafio fullstack: Django + DRF + PostgreSQL no backend e React no frontend.

## O que o sistema faz

- Login do atendente (JWT)
- Cadastro e busca de hóspedes (nome, documento, telefone)
- Lista de hóspedes no hotel e de quem tem reserva sem check-in
- Reservas, check-in e checkout
- Cálculo da conta: diária, estacionamento e taxa de checkout após 12h

## Requisitos

- Docker e Docker Compose
- Node.js 18+ (só para o frontend)

## Backend

```bash
cd backend
cp .env.example .env   # só se ainda não existir .env
docker compose up --build
```

O `web` só sobe depois do Postgres aceitar conexão (`healthcheck`). Na subida o entrypoint roda `migrate` e `seed_demo`.

API em `http://localhost:8000`.

Contas (username **ou** e-mail, senha `123`):

| Quem | Login | Onde |
|---|---|---|
| Atendente | `atendente` / `atendente@exemplo.com` | app em `http://localhost:3000` |
| Superuser | `superuser` / `superuser@exemplo.com` | Django admin em `http://localhost:8000/admin/` |

Seed:

- Frank Reynolds — no hotel, **com** carro
- Charlie Kelly — no hotel, **sem** carro
- Ronald "Mac" McDonald — reserva pendente de check-in
- Dennis Reynolds e Dee Reynolds — só ficha, sem reserva

Exemplos:

- `POST /api/v1/auth/token/` — `{ "login", "password" }` (login aceita username **ou** e-mail)
- `GET /api/v1/guests/?search=charlie`
- `GET /api/v1/guests/?status=checked_in`
- `GET /api/v1/guests/?status=reserved`
- `GET /api/v1/guests/?status=checked_out`
- `POST /api/v1/reservations/`
- `POST /api/v1/reservations/{id}/check-in/`
- `POST /api/v1/reservations/{id}/check-out/`

### Testes do backend

```bash
cd backend
docker compose run --rm --no-deps web pytest
```

## Frontend

```bash
cd frontend
npm install
npm run dev
```

Abre `http://localhost:3000`. Entre com `atendente` / `123`. Admin: `http://localhost:8000/admin/` com `superuser` / `123`.

### Testes do frontend

```bash
cd frontend
npm test
```

## Regras de preço

| Item | Dia útil | Fim de semana |
|---|---|---|
| Diária | R$ 120 | R$ 180 |
| Vaga de carro | R$ 15 | R$ 20 |

Check-in a partir das 14h: se for antes, o sistema registra e mostra um alerta.

Checkout até 12h: depois disso, +50% da diária daquele dia.
