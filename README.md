# To-Do App (puzzle anti-bot + admin)
1. `cp .env.example .env` puis modifie SECRET_KEY et ADMIN_PASSWORD
2. `docker compose up --build`
3. Ouvre http://localhost:8000
- Admin : connecte-toi avec ADMIN_USERNAME / ADMIN_PASSWORD → page /admin
- ⚠️ `docker compose down -v` SUPPRIME le volume (donc la base). Utilise `docker compose down` sans -v.
