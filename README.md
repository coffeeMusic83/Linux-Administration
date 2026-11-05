# Viikko 2: Python + MariaDB -kävijälaskuri

Flask-sovellus, joka pyörii Gunicornilla (127.0.0.1:8000) Nginxin takana polussa `/viikko2/`.
Kävijämäärä tallennetaan MariaDB:n `counter`-tauluun, joten se säilyy uudelleenkäynnistysten yli.

## Rakenne
- `app.py` – Flask-sovellus
- `schema.sql` – tietokannan luonti
- `deploy/viikko2.service` – systemd-palvelu (käynnistyy automaattisesti)
- `deploy/nginx.conf` – Nginx-konfiguraatio (`/viikko2/` → 127.0.0.1:8000)
- `.env.example` – tarvittavat ympäristömuuttujat (oikeat arvot `.env`-tiedostossa, ei repossa)
