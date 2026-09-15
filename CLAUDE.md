
## Workflow
Tu dois développer le jeu "pierre-feuille-ciseaux" en Python 3.12 sous forme d'un service défini par une API RESTful.
Tu proposeras une spéc sur la manière de jouer, les actions et les résultats et la produiras sous forme d'un document versionné "docs/spec.md" et que tu devras relire, enrichir et faire approuver par le product owner (moi) via le prompt utilisateur avant tout nouveau développement/correctif.
Un Dockerfile fonctionnel est requis (permet un build/run identique en local et en prod, indépendamment de la plateforme cloud cible) ; il n'est pas nécessaire pour le déploiement sur certaines offres managées (Cloud Run,Container Apps peuvent builder depuis le code source sans Dockerfile via buildpacks), mais on le fournit quand même pour la portabilité et la reproductibilité locale. Pas de manifestes K8s ni de Terraform tant que non demandés explicitement.

## Stack et outils
Tu utiliseras le framework FastAPI pour l'implémentation du service en Python.
Tu utiliseras les outils "uv" (pour le build et l'environement runtime Python), ruff (typage/syntaxe), mypy (vérification de types statique), github pour le développement général et pytest pour les tests unitaires (livrés) et, en usage interne, pour les tests fonctionnels de la boucle TDD (non livrés — voir section Tests).

## Environnements d'exécution
L'environnement actif est déterminé par la variable APP_ENV (dev|qa|prod), lue via pydantic-settings ; le démarrage doit échouer explicitement si APP_ENV est absente ou invalide (fail-fast), jamais de valeur par défaut 
silencieuse.
Ce qui varie par environnement : chaîne de connexion PostgreSQL (une base dédiée par environnement, aucun partage de données), niveau de log, activation de Swagger/docs (désactivé en PROD).
Un fichier ".env.example" documente toutes les variables requises (sans valeurs réelles ni secrets) pour que n'importe quel environnement soit reproductible à partir de zéro.
La correspondance branche Git → environnement, ainsi qu'un éventuel pipeline de déploiement automatisé, seront précisés dans docs/spec.md une fois un déploiement réel engagé.


## Persistance
L'API reste stateless au sens REST : aucune session ni état d'interaction conservé en mémoire du process — chaque requête est autonome et porte les identifiants nécessaires (ex. game_id, player_id).
L'état des ressources du jeu (score, stats, nom du joueur, partie en cours) est persisté dans PostgreSQL 18 (image "postgres:18"), interrogé par n'importe quelle instance à partir des identifiants transmis dans la requête.
En développement local, la base tourne via docker-compose.
Toute chaîne de connexion ou secret vient de variables d'environnement, jamais en dur dans le code.
Le schéma et les migrations (Alembic) sont documentés dans docs/architecture.md.

## Convention de routage
Tous les endpoints métier REST sont préfixés par "/rps/v1" (ex: /rps/v1/register, /rps/v1/play) — décision D5 (docs/spec.md) : la version majeure de l'API apparaît dans le chemin, pour permettre d'introduire /rps/v2/... plus tard sans casser les clients existants.
/healthz reste hors de ce préfixe (décision D2, docs/spec.md) — sonde d'infra, pas une ressource du jeu.
Le port par défaut du service sera 8080.

## Contraintes
Structure le code selon une architecture ports & adapters (domaine isolé de l'infrastructure — cf. domain/ vs api/ et db/ dans docs/architecture.md §3), et fais respecter cette frontière en CI avec import-linter plutôt que de compter uniquement sur la discipline en review.
