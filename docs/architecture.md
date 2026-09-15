# Architecture technique — Service "Pierre-Feuille-Ciseaux"

- **Version** : 1.0.0
- **Auteur** : Claude (dev), sous la responsabilité de Thomas Rouch (tech lead / PO)

Ce document décrit le "comment" : les choix d'implémentation qui réalisent
le contrat défini dans `docs/spec.md` (le "quoi"). Contrairement à
`spec.md`, il peut évoluer librement tant que le comportement observable
qui y est décrit reste inchangé — pas de ré-approbation Product Owner
requise pour ce document.

---

## 1. Modèle de données

### `players`
| Colonne      | Type          | Contraintes                  |
|--------------|---------------|-------------------------------|
| id           | UUID          | PK, généré serveur            |
| name         | VARCHAR(50)   | NOT NULL, **UNIQUE** (réalise la décision D1, docs/spec.md) |
| created_at   | TIMESTAMPTZ   | NOT NULL, défaut now()        |

### `games`
| Colonne         | Type          | Contraintes                       |
|-----------------|---------------|-------------------------------------|
| id              | UUID          | PK, généré serveur                  |
| player_id       | UUID          | FK -> players.id, NOT NULL          |
| player_move     | VARCHAR(8)    | NOT NULL, enum rock/paper/scissors  |
| opponent_move   | VARCHAR(8)    | NOT NULL, enum rock/paper/scissors  |
| result          | VARCHAR(4)    | NOT NULL, enum win/loss/draw        |
| created_at      | TIMESTAMPTZ   | NOT NULL, défaut now()              |

Les statistiques d'un joueur (`wins`, `losses`, `draws`, `games_played`)
sont **calculées à la lecture** par agrégation sur `games` (pas de colonne
dénormalisée à maintenir) — réalise la décision D4 (docs/spec.md) : plus
simple et sans risque d'incohérence.

## 2. Persistance

- PostgreSQL 18 (image `postgres:18`), une base par environnement, aucun
  partage de données.
- API stateless : chaque requête porte les identifiants nécessaires
  (`player_id`, `game_id`) ; aucun état de session en mémoire process.
- Connexion via `DATABASE_URL` (variable d'environnement), jamais de secret
  en dur.
- ORM : SQLAlchemy 2.x (style déclaratif). Migrations : **Alembic**, dossier
  `alembic/` à la racine, une migration initiale créant `players` et
  `games`.
- En local, la base tourne via `docker-compose.yml` (service `postgres:18`
  + volume nommé pour la persistance entre redémarrages).

## 3. Arborescence du projet

```
pocorange/
├── docs/
│   ├── spec.md
│   └── architecture.md
├── src/
│   └── rps/
│       ├── main.py             # factory FastAPI, montage des routers
│       ├── config.py           # Settings (pydantic-settings), Environment
│       ├── api/                # boilerplate HTTP (FastAPI)
│       │   ├── router.py       # monte /rps/v1 + /healthz
│       │   ├── deps.py         # injection des services (Depends)
│       │   ├── schemas.py      # modèles Pydantic requête/réponse
│       │   ├── health.py       # /healthz
│       │   └── v1/
│       │       ├── players.py
│       │       └── games.py
│       ├── domain/              # métier pur, sans dépendance framework
│       │   ├── rules.py        # Move, Result, resolve_round(), random_move()
│       │   ├── entities.py     # Player, Game, PlayerStats (dataclasses)
│       │   ├── exceptions.py   # PlayerNotFoundError, ...
│       │   ├── repositories.py # Protocols PlayerRepository / GameRepository
│       │   └── services.py     # PlayerService, GameService
│       └── db/                  # boilerplate persistance
│           ├── base.py         # engine/session SQLAlchemy
│           ├── models.py       # ORM PlayerModel, GameModel
│           └── repository.py   # implémentation SQL des Protocols domain
├── alembic/
│   ├── env.py
│   └── versions/
├── alembic.ini
├── tests/                       # livré : tests unitaires (domain/services, mocks)
│   ├── fakes.py                # FakePlayerRepository / FakeGameRepository
│   ├── test_rules.py
│   └── test_services.py
├── docker-compose.yml           # postgres:18 pour le développement local
├── Dockerfile
├── pyproject.toml                # dépendances + config ruff/pytest (géré par uv)
├── .env.example
├── .gitignore
└── README.md
```

`domain/` isole les règles du jeu (testables sans FastAPI ni base de
données) ; `api/` et `db/` concentrent le boilerplate technique. Principe
KISS : pas de couche d'abstraction supplémentaire (pas de repository
générique, pas de CQRS) tant que le besoin ne l'impose pas.
