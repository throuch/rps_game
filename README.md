# RPS Service — Pierre-Feuille-Ciseaux

Service RESTful du jeu pierre-feuille-ciseaux, en Python 3.12 / FastAPI.
La spécification complète et approuvée est dans [docs/spec.md](docs/spec.md).

## Prérequis

- [uv](https://docs.astral.sh/uv/) (gère lui-même l'installation de Python 3.12)
- Docker + Docker Compose, pour la base PostgreSQL locale (ou une instance
  PostgreSQL 18 déjà accessible)

## Installation

```bash
uv sync
```

## Configuration

```bash
cp .env.example .env
```

`APP_ENV` (`dev`, `qa` ou `prod`) est **obligatoire** : le service refuse de
démarrer si elle est absente ou invalide.

## Base de données locale

```bash
docker compose up -d
uv run alembic upgrade head
```

## Lancer le service

```bash
uv run uvicorn rps.main:app --reload --port 8080
```

Le service écoute sur `http://localhost:8080`.

## Découvrir l'API

- Swagger UI : `http://localhost:8080/docs` (désactivé en PROD)
- ReDoc : `http://localhost:8080/redoc`
- OpenAPI JSON : `http://localhost:8080/openapi.json`
- Healthcheck : `http://localhost:8080/healthz`

Tous les endpoints métier sont sous `/rps/v1` (détails dans
[docs/spec.md](docs/spec.md)) :

| Méthode | Endpoint                          | Description                    |
|---------|------------------------------------|---------------------------------|
| POST    | `/rps/v1/register`                 | Enregistre un joueur           |
| POST    | `/rps/v1/play`                     | Joue une manche                |
| GET     | `/rps/v1/players/{player_id}`      | Joueur + statistiques          |
| GET     | `/rps/v1/players/{player_id}/games`| Historique paginé des manches  |
| GET     | `/rps/v1/games/{game_id}`          | Détail d'une manche            |

Exemple :

```bash
curl -X POST localhost:8080/rps/v1/register \
  -H 'Content-Type: application/json' \
  -d '{"name": "Thomas"}'

curl -X POST localhost:8080/rps/v1/play \
  -H 'Content-Type: application/json' \
  -d '{"player_id": "<uuid retourné ci-dessus>", "move": "rock"}'
```

## Tests

Tests unitaires livrés (règles du jeu + services métier, sans dépendance à
une base de données réelle) :

```bash
uv run pytest
```

## Lint

```bash
uv run ruff check .
```

## Docker

```bash
docker build -t rps-service .
docker run --rm -p 8080:8080 --env-file .env rps-service
```

Si PostgreSQL tourne aussi en conteneur, adapter `DATABASE_URL` dans `.env`
pour pointer vers le nom du service Compose plutôt que `localhost`.
