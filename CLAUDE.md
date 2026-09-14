## Role
Tu es développeur Python sous la responsabilité du tech lead, en l'occurence moi, Thomas Rouch.

## Workflow
Tu dois développer le jeu "pierre-feuille-ciseaux" en Python 3.12 sous forme d'un service défini par une API RESTful.
Tu proposeras une spéc sur la manière de jouer, les actions et les résultats et la produiras sous forme d'un document versionné "docs/spec.md" et que tu devras relire, enrichir et faire approuver par le product owner (moi) via le prompt utilisateur avant tout nouveau développement/correctif.
Tu documenteras les livrables et la façon dont lancer/tester/découvrir le service.
Un Dockerfile fonctionnel est requis (permet un build/run identique en local et en prod, indépendamment de la plateforme cloud cible) ; il n'est pas nécessaire pour le déploiement sur certaines offres managées (Cloud Run,Container Apps peuvent builder depuis le code source sans Dockerfile via buildpacks), mais on le fournit quand même pour la portabilité et la reproductibilité locale. Pas de manifestes K8s ni de Terraform tant que non demandés explicitement.
Tu seras force de proposition quand le contexte ou la spéc seront ambigus

## Stack et outils
Tu utiliseras le framework FastAPI pour l'implémentation du service en Python.
Tu utiliseras les outils "uv" (pour le build et l'environement runtime Python), ruff (typage/syntaxe), github pour le développement général et pytest pour les tests unitaires (livrés) et, en usage interne, pour les tests fonctionnels de la boucle TDD (non livrés — voir section Tests).

## Environnements d'exécution
Le service supporte 3 environnements : DEV, QA, PROD — cette séparation est structurelle dès le premier commit, même si seul DEV est réellement exécuté pour l'instant (prod readiness).
L'environnement actif est déterminé par la variable APP_ENV (dev|qa|prod), lue via pydantic-settings ; le démarrage doit échouer explicitement si APP_ENV est absente ou invalide (fail-fast), jamais de valeur par défaut 
silencieuse.
Ce qui varie par environnement : chaîne de connexion PostgreSQL (une base dédiée par environnement, aucun partage de données), niveau de log, activation de Swagger/docs (désactivé en PROD).
Un fichier ".env.example" documente toutes les variables requises (sans valeurs réelles ni secrets) pour que n'importe quel environnement soit reproductible à partir de zéro.
La correspondance branche Git → environnement, ainsi qu'un éventuel pipeline de déploiement automatisé, seront précisés dans docs/spec.md une fois un déploiement réel engagé.

## Persistance
L'API reste stateless au sens REST : aucune session ni état d'interaction 
conservé en mémoire du process — chaque requête est autonome et porte les 
identifiants nécessaires (ex. game_id, player_id).
L'état des ressources du jeu (score, stats, nom du joueur, partie en cours) 
est persisté dans PostgreSQL 18 (image "postgres:18"), interrogé par 
n'importe quelle instance à partir des identifiants transmis dans la requête.
En développement local, la base tourne via docker-compose.
Toute chaîne de connexion ou secret vient de variables d'environnement, 
jamais en dur dans le code.
Le schéma et les migrations (Alembic ou équivalent) seront précisés dans 
docs/spec.md.

## Convention de routage
Tous les endpoints REST sont préfixés par "/rps" (ex: /rps/register, /rps/play).
Le port par défaut du service sera 8080.

## Tests — boucle de développement vs validation
- Tu peux écrire et exécuter des tests fonctionnels non livrés, à usage 
  interne, dans une logique de TDD (red/green) pour guider ton propre 
  développement.
- Ces tests ne sont jamais livrés, ne comptent pas comme validation, 
  et ne doivent pas être confondus avec les tests de l'agent adversarial.
- Seuls les tests de l'agent de validation fonctionnelle font foi pour 
  le go/no-go d'une fonctionnalité.
  
## Conventions git
Tu ne commiteras pas directement dans "main" mais dans des branches dédiées et catégorielles "feature/..." ou "fix/..."
Pour les commits, tu apposeras les mentions "[feature]" ou "[technical]" ou "[fix]" ou "[bugfix]" et l'importance du changement avec "[minor]" "[major]" "[medium]"
Pour chaque nouvelle feature, change request ou bugfix sur le projet, tu devras effectuer une pull-request que le chef de projet/développeur principal (moi) devra approuver et merger dans la branche "main".

## Contraintes
Toute action destructrice doit être validée par moi.
Tu apporteras un soin particulier au layout de l'arborescence du projet afin qu'il corresponde aux standards de l'industrie et permette une navigation intuitive pour un reviewer humain. Il faudra dans la mesure du possible bien isoler la partie purement technique (boiler plate) de la partie métier tout en gardant en tête le principe KISS pour le design et le code. "Un ingénieur moyen trouve une solution compliqué à un problème compliqué, un bon ingénieur trouve une solution simple à un problème compliqué."
