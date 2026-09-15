# Spécification — Service "Pierre-Feuille-Ciseaux"

- **Statut** : 🟢 Approuvée (Product Owner) — cf. §6
- **Version** : 0.4.0 (extraction de "Modèle de données", "Persistance" et
  "Arborescence du projet" vers docs/architecture.md, dédié au "comment" ;
  aucune décision de fond changée)
- **Auteur** : Claude (dev), sous la responsabilité de Thomas Rouch (tech lead / PO)

Ce document décrit le "quoi" : le comportement attendu et le contrat
technique du service — versionné, il fait foi, et toute évolution doit être
reflétée ici et re-approuvée avant implémentation. Les choix
d'implémentation ("comment") vivent séparément dans `docs/architecture.md`.

---

## 1. Fonctionnalités

### Jouer une manche
En tant que joueur enregistré, je veux soumettre un coup (pierre, feuille
ou ciseaux) contre la maison, afin d'obtenir immédiatement le résultat de
la manche.

Un joueur enregistré affronte "la maison" (le serveur), qui joue un coup
aléatoire à chaque manche. Il n'y a pas de mode joueur-contre-joueur en V1
(cf. §5 Hors périmètre).

Coups possibles : `rock`, `paper`, `scissors`.

Résolution d'une manche (du point de vue du joueur) :

| Joueur     | Adversaire | Résultat |
|------------|------------|----------|
| rock       | scissors   | win      |
| scissors   | paper      | win      |
| paper      | rock       | win      |
| identique  | identique  | draw     |
| sinon      | —          | loss     |

Chaque manche est **complète et autonome** (pas de notion de "partie en
plusieurs manches" en V1) : le joueur soumet un coup, le serveur tire le
sien, le résultat est calculé et persisté immédiatement. C'est la ressource
"game" la plus simple qui satisfait le besoin (KISS) ; une notion de match
en plusieurs manches pourra être ajoutée plus tard sans casser cette base
(cf. §5).

### S'enregistrer comme joueur
En tant que nouveau joueur, je veux m'enregistrer avec un nom, afin de
pouvoir ensuite jouer et suivre mes statistiques.

Le nom choisi doit être **unique** — une tentative d'enregistrement avec un
nom déjà pris est refusée (cf. décision D1).

La date d'inscription du joueur doit être persistée.

### Consulter mes statistiques
En tant que joueur, je veux consulter mes statistiques (parties jouées,
victoires, défaites, égalités), afin de suivre ma progression.

Les statistiques reflètent l'ensemble des manches jouées par le joueur,
calculées à la demande plutôt que stockées (cf. décision D4).

### Consulter l'historique de mes manches
En tant que joueur, je veux consulter la liste de mes manches passées, afin
de revoir mon historique de jeu.

Liste paginée (`limit` défaut 20, max 100 ; `offset` défaut 0).

> ⚠️ **Écart trouvé pendant la réorg** : l'ordre de tri de cette liste
> n'est précisé nulle part dans la version précédente du document. À
> trancher explicitement — probablement le plus récent en premier — avant/à
> la prochaine évolution de cette fonctionnalité, sauf si l'implémentation
> actuelle a déjà tranché ce point sans que ce soit remonté ici.

### Consulter le détail d'une manche
En tant que joueur, je veux consulter le détail d'une manche précise, afin
de revoir un résultat spécifique.

### Hall of fame
En tant que joueur, je veux consulter le classement des joueurs par taux de victoire, afin de comparer mes performances aux autres.
Comportement attendu : liste des joueurs (nom, victoires, défaites, total, % de réussite), date d'inscription, triée par % décroissant, recalcul systématique.
Cas limite : un joueur sans partie jouée apparaît dans le classement avec des statistiques nulles.

## 2. Contrat technique

Tous les endpoints métier sont sous `/rps/v1/...` (cf. décision D5 : la
version majeure de l'API apparaît dans le chemin, ce qui permettra
d'introduire `/rps/v2/...` plus tard sans casser les clients existants).

Toutes les réponses sont en JSON. Les erreurs suivent le format standard
FastAPI `{"detail": "..."}`.

### `POST /rps/v1/register`
cf. Fonctionnalité "S'enregistrer comme joueur" (§1).

Requête :
```json
{ "name": "Thomas" }
```
Réponses :
- `201 Created`
```json
{ "player_id": "uuid", "name": "Thomas", "created_at": "2026-09-14T10:00:00Z" }
```
- `409 Conflict` — un joueur existe déjà avec ce `name`.
- `422 Unprocessable Entity` — nom absent/vide/trop long.

### `POST /rps/v1/play`
cf. Fonctionnalité "Jouer une manche" (§1).

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

### `GET /rps/v1/players/{player_id}`
cf. Fonctionnalité "Consulter mes statistiques" (§1).

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

### `GET /rps/v1/players/{player_id}/games`
cf. Fonctionnalité "Consulter l'historique de mes manches" (§1).

Query params `limit` défaut 20 max 100, `offset` défaut 0.

- `200 OK`
```json
{ "items": [ { "...": "cf. objet game de /rps/v1/play" } ], "total": 12 }
```
- `404 Not Found` si le joueur n'existe pas.

### `GET /rps/v1/games/{game_id}`
cf. Fonctionnalité "Consulter le détail d'une manche" (§1).

- `200 OK` (même forme que la réponse de `/rps/v1/play`, avec `player_id`).
- `404 Not Found`.

### Hall of fame 
cf. Fonctionnalités "Hall of Fame" (§1)
GET /rps/hof → liste triée par pourcentage de victoire (arrondi) décroissant, champs : nom, victoires, défaites, total, pourcentage.

### `GET /healthz`
Hors `/rps` (décision D2 validée) — sonde d'infra, sans Fonctionnalité
correspondante côté joueur.

Vérification de disponibilité (liveness/readiness), sans dépendance DB pour
la liveness. Retourne `200 OK` `{"status": "ok"}`.

## 3. Environnements (DEV / QA / PROD)

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

## 4. Tests

- **Livrés** (`tests/`, pytest) : tests unitaires sur `domain/rules.py`
  (résolution des manches) et `domain/services.py` (logique métier, avec
  repository mocké). Pas de test d'intégration base de données livré.
- **Internes, non livrés** : tests fonctionnels (API + DB réelle) utilisés
  en boucle TDD (red/green) pour guider le développement. Ils ne comptent
  pas comme validation.
- **Validation go/no-go** : uniquement les tests de l'agent de validation
  fonctionnelle (externe à ce dépôt de tests).

## 5. Hors périmètre V1 (extensions possibles futures)

- Mode joueur-contre-joueur (matchmaking, deux vrais joueurs sur une même
  partie).
- Notion de "match" en plusieurs manches avec condition de victoire
  (best-of-N).
- Authentification / autorisation (aucune en V1 — `player_id` suffit à
  s'identifier, pas de notion de compte sécurisé).
- Manifestes Kubernetes, Terraform, pipeline CI/CD réel.

## 6. Décisions validées (PO — 2026-09-14)

- **D1** — ✅ `name` du joueur est **unique** ; tentative d'enregistrement
  avec un nom déjà pris → `409 Conflict`. Contrainte `UNIQUE` en base sur
  `players.name` (implémentation détaillée dans docs/architecture.md).
- **D2** — ✅ `/healthz` reste hors du préfixe `/rps` (sonde d'infra, pas une
  ressource du jeu).
- **D3** — ✅ Une "game" = une manche unique et immédiate (pas de
  multi-manches en V1), cf. §1.
- **D4** — ✅ Statistiques calculées à la volée (agrégation SQL) plutôt que
  dénormalisées sur `players` (implémentation détaillée dans
  docs/architecture.md).
- **D5** — ✅ (ajout) L'API est versionnée dans le chemin : tous les
  endpoints métier passent de `/rps/...` à `/rps/v1/...`. `/healthz` n'est
  pas versionné (D2).

Dès que ce document est approuvé. L'implémentation peut démarrer sur cette base.
