# GroceryApp service commands

These instructions are for the Ubuntu installation at `/home/clegane/GroceryApp`,
running as user `clegane` with the existing `.venv`. The web app listens on port
`8081`; its default writable application data is stored outside the Git checkout in
`~/.local/share/groceryapp/`.

## Install the systemd service (one time)

First make sure the app is not still running manually in a terminal. In the terminal
where you ran `python web_app.py`, press `Ctrl+C`.

From the project directory, install the service unit:

```bash
cd ~/GroceryApp
sudo cp groceryapp.service /etc/systemd/system/groceryapp.service
sudo systemctl daemon-reload
sudo systemctl enable --now groceryapp
```

Check that it started:

```bash
sudo systemctl status groceryapp --no-pager
curl -I http://127.0.0.1:8081
```

The status should say `active (running)`; the local HTTP request should return a successful
response, usually `HTTP/1.1 200 OK`.

## Start, stop, and restart

Start GroceryApp:

```bash
sudo systemctl start groceryapp
```

Stop GroceryApp:

```bash
sudo systemctl stop groceryapp
```

Restart it after updating code:

```bash
sudo systemctl restart groceryapp
```

Check status:

```bash
sudo systemctl status groceryapp --no-pager
```

Show the last 50 log lines:

```bash
sudo journalctl -u groceryapp -n 50 --no-pager
```

Follow logs live (press `Ctrl+C` to stop following; this does not stop GroceryApp):

```bash
sudo journalctl -u groceryapp -f
```

## Automatic startup and recovery

Enable automatic startup at boot:

```bash
sudo systemctl enable groceryapp
```

Disable automatic startup (does not by itself stop a currently running app):

```bash
sudo systemctl disable groceryapp
```

The service uses `Restart=on-failure`, so systemd attempts to restart it after a crash.
It cannot run while the computer is powered off or suspended.

## Update from the `develop` branch

The working branch for changes is `develop`; do not merge it into `master` unless you
choose to. First commit or stash local changes you want to keep. GroceryApp's web interface
can edit recipe files inside the checkout, so check `git status` before pulling and preserve
any recipe edits.

```bash
cd ~/GroceryApp
git status
git fetch origin
git switch develop
git pull --ff-only
sudo systemctl restart groceryapp
sudo systemctl status groceryapp --no-pager
```

If the local `develop` branch does not exist yet, create it to track the remote branch once:

```bash
git fetch origin
git switch --track origin/develop
```

After updating, test the web app locally:

```bash
curl -I http://127.0.0.1:8081
```

If the service fails to start, inspect its logs:

```bash
sudo journalctl -u groceryapp -n 100 --no-pager
```

## Data and network notes

- The web database, theme settings, Flask secret, and recipe-usage timestamps default to
  `~/.local/share/groceryapp/`; keep this directory when updating code.
- Recipe text files and store configuration live in the project checkout. Recipe edits made
  in the web UI therefore appear as Git changes; preserve them before pulling updates.
- The app listens on port `8081`. From another device on your home Wi-Fi, use
  `http://192.168.86.250:8081` unless you configure an HTTPS proxy for GroceryApp.
- Keep access restricted to your trusted home network. Do not configure router port forwarding
  for this service.
