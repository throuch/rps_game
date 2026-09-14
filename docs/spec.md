# Spécification — Service "Pierre-Feuille-Ciseaux"

- **Statut** : 🟡 En attente de validation (Product Owner)
- **Version** : 0.1.0
- **Auteur** : Claude (dev), sous la responsabilité de Thomas Rouch (tech lead / PO)

Ce document est versionné et fait foi. Toute évolution du jeu ou de l'API
doit être reflétée ici et re-approuvée avant implémentation.

---

## 1. Règles du jeu

Un joueur enregistré affronte "la maison" (le serveur), qui joue un coup
aléatoire à chaque manche. Il n'y a pas de mode joueur-contre-joueur en V1
(cf. §7 Hors périmètre).

Coups possibles : `rock`, `paper`, `scissors`.

Résolution d'une manche (du point de vue du joueur) :

| Joueur     | Adversaire | Résultat |
|------------|------------|----------|
| rock       | scissors   | win      |
| scissors   | paper      | win      |
| paper      | rock       | win      |
| identique  | identique  | draw     |
| sinon      | —          | loss     |

Chaque appel à `/rps/play` constitue une **manche complète et autonome**
(pas de notion de "partie en plusieurs manches" en V1) : le joueur soumet un
coup, le serveur tire le sien, le résultat est calculé et persisté
immédiatement. C'est la ressource "game" la plus simple qui satisfait le
besoin (KISS) ; une notion de match en plusieurs manches pourra être ajoutée
plus tard sans casser cette base (cf. §7).

## 2. Modèle de données

### `players`
| Colonne      | Type          | Contraintes                  |
|--------------|---------------|-------------------------------|
| id           | UUID          | PK, généré serveur            |
| name         | VARCHAR(50)   | NOT NULL (pas d'unicité, cf. décision D1) |
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
dénormalisée à maintenir) — plus simple et sans risque d'incohérence.

## 3. API — endpoints (préfixe `/rps`)

Toutes les réponses sont en JSON. Les erreurs suivent le format standard
FastAPI `{"detail": "..."}`.

### `POST /rps/register`
Enregistre un nouveau joueur.

Requête :
```json
{ "name": "Thomas" }
```
Réponses :
- `201 Created`
```json
{ "player_id": "uuid", "name": "Thomas", "created_at": "2026-09-14T10:00:00Z" }
```
- `422 Unprocessable Entity` — nom absent/vide/trop long.

### `POST /rps/play`
Joue une manche pour un joueur existant.

Requête :
```json
{ "player_id": "uuid", "move": "rock" }
```
Réponses :
- `201 Created`
```json
{
  "game_id": "uuid",
  "player_move": "rock",
  "opponent_move": "scissors",
  "result": "win",
  "created_at": "2026-09-14T10:00:05Z"
}
```
- `404 Not Found` — `player_id` inconnu.
- `422 Unprocessable Entity` — `move` absent ou hors énumération.

### `GET /rps/players/{player_id}`
Retourne le joueur et ses statistiques agrégées.

- `200 OK`
```json
{
  "player_id": "uuid",
  "name": "Thomas",
  "created_at": "2026-09-14T10:00:00Z",
  "stats": { "games_played": 12, "wins": 5, "losses": 4, "draws": 3 }
}
```
- `404 Not Found`.

### `GET /rps/players/{player_id}/games`
Historique paginé des manches d'un joueur (query params `limit` défaut 20
max 100, `offset` défaut 0).

- `200 OK`
```json
{ "items": [ { "...": "cf. objet game de /rps/play" } ], "total": 12 }
```
- `404 Not Found` si le joueur n'existe pas.

### `GET /rps/games/{game_id}`
Détail d'une manche.

- `200 OK` (même forme que la réponse de `/rps/play`, avec `player_id`).
- `404 Not Found`.

### `GET /healthz` (hors `/rps`, cf. décision D2)
Vérification de disponibilité (liveness/readiness), sans dépendance DB pour
la liveness. Retourne `200 OK` `{"status": "ok"}`.

## 4. Environnements (DEV / QA / PROD)

- Variable `APP_ENV` (`dev|qa|prod`), lue via `pydantic-settings`. Absence
  ou valeur invalide → échec au démarrage (fail-fast), aucune valeur par
  défaut.
- Ce qui varie par environnement :
  - `DATABASE_URL` : une base PostgreSQL dédiée par environnement.
  - Niveau de log (`LOG_LEVEL`) : `DEBUG` en dev, `INFO` en qa/prod par défaut
    (surchargeable).
  - Documentation OpenAPI (`/docs`, `/redoc`, `/openapi.json`) : activée en
    dev/qa, **désactivée en prod**.
- Seul DEV est réellement exécuté à ce stade ; QA/PROD restent structurels
  (config prête, non déployée).
- Le port d'écoute par défaut est `8080` (surchargeable via `APP_PORT`).
- Correspondance branche Git → environnement et pipeline CI/CD : **à
  préciser dans ce document au moment d'un premier déploiement réel** (hors
  périmètre V1).

## 5. Persistance

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

## 6. Arborescence du projet (proposée)

```
pocorange/
├── docs/
│   └── spec.md
├── src/
│   └── rps/
│       ├── main.py            # factory FastAPI, montage des routers
│       ├── config.py          # Settings (pydantic-settings), Environment
│       ├── api/                # boilerplate HTTP (FastAPI)
│       │   ├── router.py
│       │   ├── players.py
│       │   ├── games.py
│       │   ├── health.py
│       │   └── schemas.py     # modèles Pydantic requête/réponse
│       ├── domain/             # métier pur, sans dépendance framework
│       │   ├── rules.py       # Move, Result, resolve_round()
│       │   └── services.py    # PlayerService, GameService
│       └── db/                 # boilerplate persistance
│           ├── base.py        # engine/session SQLAlchemy
│           ├── models.py      # ORM Player, Game
│           └── repository.py
├── alembic/
│   ├── env.py
│   └── versions/
├── alembic.ini
├── tests/                      # livré : tests unitaires (domain/services, mocks)
│   ├── conftest.py
│   ├── test_rules.py
│   └── test_services.py
├── docker-compose.yml          # postgres:18 pour le développement local
├── Dockerfile
├── pyproject.toml               # dépendances + config ruff (géré par uv)
├── .env.example
├── .gitignore
└── README.md
```

`domain/` isole les règles du jeu (testables sans FastAPI ni base de
données) ; `api/` et `db/` concentrent le boilerplate technique. Principe
KISS : pas de couche d'abstraction supplémentaire (pas de repository
générique, pas de CQRS) tant que le besoin ne l'impose pas.

## 7. Tests

- **Livrés** (`tests/`, pytest) : tests unitaires sur `domain/rules.py`
  (résolution des manches) et `domain/services.py` (logique métier, avec
  repository mocké). Pas de test d'intégration base de données livré.
- **Internes, non livrés** : tests fonctionnels (API + DB réelle) utilisés
  en boucle TDD (red/green) pour guider le développement. Ils ne comptent
  pas comme validation.
- **Validation go/no-go** : uniquement les tests de l'agent de validation
  fonctionnelle (externe à ce dépôt de tests).

## 8. Hors périmètre V1 (extensions possibles futures)

- Mode joueur-contre-joueur (matchmaking, deux vrais joueurs sur une même
  partie).
- Notion de "match" en plusieurs manches avec condition de victoire
  (best-of-N).
- Authentification / autorisation (aucune en V1 — `player_id` suffit à
  s'identifier, pas de notion de compte sécurisé).
- Manifestes Kubernetes, Terraform, pipeline CI/CD réel.

## 9. Décisions proposées à valider (PO)

- **D1** — `name` du joueur n'est pas unique (deux joueurs peuvent
  s'appeler "Thomas") ; seul `player_id` identifie un joueur. *Alternative :
  imposer l'unicité du nom (409 Conflict si pris).*
- **D2** — `/healthz` est placé **hors** du préfixe `/rps` car ce n'est pas
  une ressource du jeu mais une sonde d'infrastructure. *Alternative : le
  mettre sous `/rps/health` pour respecter la règle "tous les endpoints sous
  /rps" à la lettre.*
- **D3** — Une "game" = une manche unique et immédiate (pas de multi-manches
  en V1), cf. §7.
- **D4** — Statistiques calculées à la volée (agrégation SQL) plutôt que
  dénormalisées sur `players`.

---

**Merci de valider ce document (ou de m'indiquer les points à amender) avant
que je démarre l'implémentation.**
