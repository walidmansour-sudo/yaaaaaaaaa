# 📝 To-Do List sécurisée avec Flask et Docker

## 📌 Présentation du projet

Ce projet consiste à créer une application web de gestion de tâches (To-Do List) avec Python et Flask, puis à la conteneuriser avec Docker et Docker Compose.

Chaque utilisateur crée son propre compte après avoir réussi un petit jeu (puzzle) qui sert à bloquer les robots. Une fois connecté, il accède à sa liste de tâches personnelle. Un administrateur dispose d'une page spéciale qui affiche le nombre d'utilisateurs inscrits, leurs noms et leur date d'inscription.

Ce projet a été réalisé dans le but de comprendre comment fonctionne une application web avec comptes utilisateurs et base de données, et comment l'exécuter dans des conteneurs Docker.

## 🎯 Objectifs

* Découvrir le framework Flask et ses routes.
* Créer une interface web avec HTML, CSS et JavaScript.
* Mettre en place une inscription et une connexion sécurisées (mots de passe hachés).
* Protéger l'inscription contre les robots avec un puzzle vérifié côté serveur.
* Stocker les utilisateurs et leurs tâches dans une base de données SQLite.
* Créer une page d'administration réservée à l'admin.
* Comprendre le rôle d'un Dockerfile, d'un `.dockerignore` et d'un `docker-compose.yml`.
* Conserver les données grâce à un volume Docker.

## 🛠️ Technologies utilisées

* *Python 3.12* : langage de programmation.
* *Flask* : framework Python pour créer l'application web.
* *Gunicorn* : serveur d'application utilisé dans le conteneur.
* *SQLite* : base de données (fichier unique, deux tables : `users` et `todos`).
* *HTML, CSS, JavaScript* : interface et logique du puzzle.
* *Docker et Docker Compose* : construction de l'image et exécution du conteneur.
* *Visual Studio Code* : environnement de développement.

## 📁 Structure du projet

```text
todo-app/
│
├── app.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── .env.example
├── README.md
│
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── todos.html
│   └── admin.html
│
└── static/
    ├── puzzle.js
    └── style.css
```

### Description des fichiers

* `app.py` : contient le code Python, les routes Flask, la base de données, l'authentification et la vérification du puzzle.
* `requirements.txt` : liste les dépendances Python (Flask et Gunicorn).
* `Dockerfile` : décrit les instructions pour construire l'image Docker.
* `docker-compose.yml` : décrit le service, le port, les variables d'environnement et le volume.
* `.dockerignore` : liste les fichiers à ne pas copier dans l'image (`.env`, bases locales, caches…).
* `.env.example` : modèle du fichier `.env` qui contient les secrets.
* `templates/` : pages HTML (connexion, inscription, to-do list, admin).
* `static/puzzle.js` : logique du puzzle côté navigateur.
* `static/style.css` : mise en forme de l'interface.
* `README.md` : présente le projet et explique comment l'exécuter.

## ⚙️ Fonctionnalités

* **Puzzle anti-bot** : cliquer les cases de 1 à 6 dans l'ordre avant de s'inscrire ou de se connecter. Le résultat est vérifié côté serveur (bon ordre et temps minimum).
* **Inscription et connexion** avec nom d'utilisateur et mot de passe (haché, jamais stocké en clair).
* **To-Do List personnelle** : ajouter, cocher/décocher et supprimer des tâches. Chaque utilisateur voit uniquement ses tâches.
* **Page admin** : nombre total d'utilisateurs, nom, date d'inscription (UTC) et nombre de tâches de chacun. Les mots de passe ne sont jamais affichés.
* **Données persistantes** : la base est stockée dans un volume Docker.

*Remarque :* contrairement à une simple liste en mémoire, les données sont enregistrées dans une base de données et ne sont pas perdues quand le conteneur redémarre. Elles sont supprimées uniquement si le volume est supprimé (voir la partie Sauvegarde).

## 🔐 Configuration (fichier `.env`)

Avant de lancer le projet, créer le fichier `.env` à partir du modèle :

```bash
cp .env.example .env            # Linux / macOS
Copy-Item .env.example .env     # Windows PowerShell
```

Puis modifier les valeurs :

| Variable | Description |
| --- | --- |
| `SECRET_KEY` | Clé secrète qui signe les cookies de session. Utiliser une longue chaîne aléatoire. |
| `ADMIN_USERNAME` | Nom d'utilisateur du compte admin (par défaut : `admin`). |
| `ADMIN_PASSWORD` | Mot de passe du compte admin. Choisir un mot de passe solide. |

Générer une bonne clé secrète :

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

*Remarque :* le compte admin est créé une seule fois, au premier démarrage avec une base vide. Modifier `ADMIN_PASSWORD` plus tard ne change pas le mot de passe d'un admin déjà créé.

## 🚀 Installation et exécution sans Docker

### 1. Installer les dépendances

```bash
py -m pip install -r requirements.txt
```

### 2. Définir les variables et lancer l'application

```powershell
$env:DB_PATH="./data/app.db"; $env:SECRET_KEY="dev"; $env:ADMIN_PASSWORD="admin123"
py -m flask --app app run --debug
```

Sous Linux/macOS : `export DB_PATH=./data/app.db SECRET_KEY=dev ADMIN_PASSWORD=admin123` puis `flask --app app run --debug`.

### 3. Accéder à l'application

Ouvrir un navigateur et accéder à :

http://localhost:5000

## 🐳 Exécution avec Docker Compose

### 1. Se placer dans le dossier du projet

Il faut être dans le dossier qui contient `docker-compose.yml` (vérifier avec `dir` ou `ls`).

### 2. Construire l'image et démarrer le conteneur

```bash
docker compose up -d --build
```

Cette commande construit l'image à partir du `Dockerfile`, crée le volume de données, puis crée et démarre le conteneur.

Explication :

* `up` : crée et démarre les conteneurs.
* `-d` : exécute le conteneur en arrière-plan.
* `--build` : reconstruit l'image avant de démarrer.

### 3. Vérifier le conteneur

```bash
docker compose ps
```

### 4. Voir les logs

```bash
docker compose logs -f
```

### 5. Accéder à l'application

Ouvrir :

http://localhost:8000

### 6. Accéder à la page admin

1. Aller sur http://localhost:8000/login.
2. Résoudre le puzzle.
3. Se connecter avec `ADMIN_USERNAME` et `ADMIN_PASSWORD` du fichier `.env`.
4. L'admin est redirigé automatiquement vers `/admin`.

Un utilisateur normal qui essaie d'ouvrir `/admin` reçoit une erreur `403 Forbidden`.

## 🔄 Mettre à jour l'application

Lorsqu'on modifie le code source ou les fichiers HTML, il faut reconstruire l'image pour intégrer les changements.

```bash
docker compose up -d --build
```

Compose remplace automatiquement l'ancien conteneur par un nouveau. Les données sont conservées car elles sont dans le volume.

Pour arrêter l'application :

```bash
docker compose down
```

> ⚠️ **Ne jamais ajouter `-v`** (`docker compose down -v`) sauf si on veut supprimer la base de données : cette option supprime le volume et donc tous les comptes et toutes les tâches.

## 💾 Sauvegarde et restauration de la base

```bash
# Sauvegarde (le conteneur doit tourner)
mkdir backups
docker compose cp web:/data/app.db ./backups/app.db

# Restauration
docker compose cp ./backups/app.db web:/data/app.db
docker compose restart
```

Faire une sauvegarde avant toute commande qui pourrait supprimer le volume.

## 🗄️ Base de données

**Table `users`**

| Colonne | Description |
| --- | --- |
| `id` | Identifiant unique. |
| `username` | Nom d'utilisateur (unique). |
| `password_hash` | Mot de passe haché. |
| `is_admin` | `1` pour l'admin, `0` sinon. |
| `created_at` | Date d'inscription (UTC). |

**Table `todos`**

| Colonne | Description |
| --- | --- |
| `id` | Identifiant unique. |
| `user_id` | Propriétaire de la tâche (lié à `users.id`). |
| `title` | Texte de la tâche. |
| `done` | `0` (à faire) ou `1` (terminée). |
| `created_at` | Date de création (UTC). |

Chaque requête sur les tâches filtre sur l'utilisateur connecté : c'est ce qui permet à chacun d'accéder uniquement à sa propre liste.

## 🧠 Concepts Docker appris

| Concept | Description |
| --- | --- |
| Image Docker | Modèle figé utilisé pour créer un conteneur. |
| Conteneur | Instance en cours d'exécution créée à partir d'une image. |
| Dockerfile | Fichier qui décrit la construction d'une image. |
| `.dockerignore` | Fichier qui liste ce qu'il ne faut pas copier dans l'image (secrets, caches, bases locales). |
| Docker Compose | Outil qui décrit et lance les conteneurs avec un seul fichier. |
| Volume | Espace de stockage géré par Docker, séparé du conteneur, qui garde les données. |
| Mapping de ports | `"8000:8000"` relie le port de l'ordinateur au port du conteneur. |
| Variables d'environnement | Valeurs (secrets, réglages) fournies au conteneur au démarrage via `.env`. |
| Couches et cache | Chaque instruction du Dockerfile est mise en cache pour accélérer les reconstructions. |
| `docker compose up -d --build` | Construit l'image et démarre le conteneur en arrière-plan. |
| `docker compose ps` | Affiche les conteneurs du projet. |
| `docker compose logs -f` | Affiche les logs en direct. |
| `docker compose down` | Arrête et supprime le conteneur (volume conservé). |
| `docker compose down -v` | Supprime aussi le volume (données perdues). |
| `docker compose exec web sh` | Ouvre un terminal dans le conteneur. |
| `docker images` | Affiche les images locales. |
| `docker volume ls` | Affiche les volumes. |

### Le Dockerfile expliqué

```dockerfile
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN mkdir -p /data
EXPOSE 8000
CMD ["gunicorn", "-w", "1", "--threads", "4", "-b", "0.0.0.0:8000", "app:app"]
```

* `FROM` : image de départ avec Python 3.12 (version `slim`, plus légère).
* `ENV` : évite les fichiers `.pyc` inutiles et affiche les logs immédiatement.
* `WORKDIR` : dossier de travail dans le conteneur.
* `COPY requirements.txt .` puis `RUN pip install` : les dépendances sont installées **avant** de copier le code. Ainsi, quand on modifie seulement `app.py`, Docker réutilise le cache et la reconstruction est rapide.
* `COPY . .` : copie le reste du projet.
* `RUN mkdir -p /data` : crée le dossier de la base de données.
* `EXPOSE 8000` : indique le port utilisé par l'application.
* `CMD` : lance Gunicorn sur `0.0.0.0:8000`. L'adresse `0.0.0.0` est nécessaire pour que le navigateur puisse atteindre l'application depuis l'extérieur du conteneur. Un seul worker est utilisé car SQLite supporte mal les écritures simultanées de plusieurs processus.

### Le fichier docker-compose.yml expliqué

```yaml
services:
  web:
    build: .
    ports:
      - "8000:8000"
    env_file: .env
    environment:
      DB_PATH: /data/app.db
    volumes:
      - app_data:/data
    restart: unless-stopped

volumes:
  app_data:
```

* `build: .` : construit l'image avec le Dockerfile du dossier.
* `ports` : le port 8000 de l'ordinateur est relié au port 8000 du conteneur (format `ordinateur:conteneur`). Pour utiliser le port 8080 : `"8080:8000"`.
* `env_file` : charge les variables du fichier `.env`.
* `environment` : indique où se trouve la base de données.
* `volumes` : monte le volume `app_data` dans `/data`, ce qui garde la base même si le conteneur est supprimé.
* `restart: unless-stopped` : redémarre le conteneur automatiquement, sauf s'il a été arrêté volontairement.

### Pourquoi un volume ?

Le contenu d'un conteneur est temporaire : quand il est supprimé ou reconstruit, tout ce qu'il contenait disparaît. Le volume est stocké en dehors du conteneur, donc la base SQLite survit.

| Commande | Conteneur | Données (volume) |
| --- | --- | --- |
| `docker compose stop` | Arrêté | Conservées |
| `docker compose down` | Supprimé | Conservées |
| `docker compose up -d --build` | Recréé | Conservées |
| `docker compose down -v` | Supprimé | **Supprimées** |

Le nom du volume dépend du nom du dossier du projet (par exemple `todo-app_app_data`). Lancer le projet depuis un dossier au nom différent crée un nouveau volume vide.

## 🛡️ Sécurité

* Mots de passe hachés.
* Requêtes SQL paramétrées (protection contre l'injection SQL).
* Échappement automatique des pages (protection contre le XSS).
* Puzzle vérifié côté serveur et utilisable une seule fois.
* Chaque utilisateur accède uniquement à ses propres tâches.
* Le fichier `.env` n'est pas copié dans l'image grâce au `.dockerignore`.

Avant une mise en ligne : utiliser un mot de passe admin solide, servir l'application en HTTPS, limiter les tentatives de connexion et ajouter une protection CSRF. Ce puzzle arrête les robots simples, mais ne remplace pas un vrai CAPTCHA face à un attaquant déterminé.

## 🧯 Problèmes fréquents

| Problème | Solution |
| --- | --- |
| `no configuration file provided: not found` | Se placer dans le dossier qui contient `docker-compose.yml`. |
| `env file .env not found` | Créer le fichier `.env` à partir de `.env.example`. |
| `not a valid editable requirement` | `requirements.txt` ne doit contenir que `flask==3.0.3` et `gunicorn==22.0.0`, sans `-e` au début d'une ligne. |
| `port is already allocated` | Le port 8000 est utilisé : changer en `"8080:8000"` dans `docker-compose.yml`. |
| Impossible de se connecter en admin | Utiliser le mot de passe défini au premier démarrage (l'admin n'est créé qu'une fois). |
| Les modifications du code n'apparaissent pas | Reconstruire avec `docker compose up -d --build`. |
| Les données ont disparu | Le volume a été supprimé (`down -v`) ou le dossier du projet a changé de nom. |

## 💡 Pistes d'amélioration

* Changement de mot de passe et suppression de compte.
* Actions admin : supprimer un utilisateur, réinitialiser un mot de passe.
* Dates d'échéance et catégories pour les tâches.
* Base PostgreSQL dans un second conteneur.
* Sauvegardes automatiques.
* Interface en plusieurs langues.

## 📚 Conclusion

Ce projet m'a permis de découvrir le développement web avec Flask : routes, templates, sessions, authentification et base de données SQLite. Il m'a aussi permis de comprendre la conteneurisation avec Docker : construire une image, utiliser un `.dockerignore`, orchestrer le tout avec Docker Compose, et conserver les données grâce à un volume.

Ce projet constitue une étape vers la compréhension du déploiement d'applications sécurisées dans des environnements conteneurisés.

## 👩‍💻 Auteur

Projet réalisé dans le cadre de l'apprentissage de Docker et du développement web avec Python et Flask.
