# GroceryApp web edition (first pass)

This adds a mobile-friendly Flask interface alongside the existing Tkinter desktop app. It reuses the existing recipe parser, ingredient aggregation, store ordering, and recipe-usage history. It does not replace or remove the desktop entry point.

## Included in this first pass

- Filter recipes by tags and select a weekly menu from a phone or computer.
- Open recipe details and instructions.
- Generate a store-ordered grocery list from the selected recipes.
- Check off shopping items; checked state persists in SQLite across page reloads.
- Keep web state in `~/.local/share/groceryapp/` by default, separate from the source checkout.
- Use port **8081**, leaving Circuit Coach on port 8080.
- No Todoist or Trello API calls are triggered by the web interface yet.

## Run it on Ubuntu for a first test

From the directory where you want to keep the app:

```bash
mkdir -p ~/apps
sudo apt update
sudo apt install -y python3-venv
git clone https://github.com/fryeguy52/GroceryApp.git ~/apps/GroceryApp
cd ~/apps/GroceryApp
git switch web-app-first-pass
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt -r web-requirements.txt
python web_app.py
```

On the Ubuntu machine, open `http://127.0.0.1:8081`. To find its LAN IP, open a second terminal and run:

```bash
hostname -I
```

On a phone connected to the same home Wi-Fi, open `http://UBUNTU-LAN-IP:8081` (replace the example with the actual IP).

The Flask development server is only intended for initial testing on a trusted home network. For regular use, use the Gunicorn/systemd setup below.

## Run it as a background service

1. Make sure the checkout is at `/home/YOUR_USER/apps/GroceryApp` and the virtual environment is installed as above.
2. Copy `deploy/groceryapp.service.example` to `/etc/systemd/system/groceryapp.service`.
3. Replace both instances of `YOUR_USER` with your Ubuntu username.
4. Start it:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now groceryapp
sudo systemctl status groceryapp
```

Useful commands:

```bash
sudo systemctl restart groceryapp
sudo systemctl stop groceryapp
sudo journalctl -u groceryapp -f
```

## Firewall and network boundary

The service listens on port 8081. If UFW is enabled, allow access only from your home LAN subnet. For example, **only if** your LAN uses `192.168.1.x`:

```bash
sudo ufw allow from 192.168.1.0/24 to any port 8081 proto tcp
sudo ufw status
```

Use the actual subnet configured on your router; do not copy the example blindly. Do not configure router port forwarding for this app. Binding to all interfaces is paired with a LAN-restricted firewall rule; if you prefer, the service can instead bind to the Ubuntu machine's specific LAN IP.

## Data and migration notes

- Web database: `~/.local/share/groceryapp/groceryapp-web.sqlite3`
- Recipe-usage database: `~/.local/share/groceryapp/recipe_time_stamps.db`
- A copy of the repository's existing `recipe_time_stamps.db` is made on first startup if no web-specific usage database exists. Later web updates write to the data directory, not to the tracked repository database.
- Recipes and store configuration continue to live in `recipes/` and `src/`.
- Back up `~/.local/share/groceryapp/` before moving or reinstalling the app.

## Current limits / next steps

This is a first pass, not yet a full replacement for every desktop workflow. The web UI currently targets one shared household menu and shopping list. It does not yet edit recipes or store departments, expose usage-history reports, or call Todoist/Trello. Before making it available beyond a trusted home LAN, add authentication and review the deployment/security setup. The app includes CSRF checks for form submissions, but that is not a substitute for authentication.
