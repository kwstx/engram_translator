# Updating & Uninstalling

How to update Engram to the latest version, roll back if something breaks, and cleanly remove everything when you're done.

---

## Updating

### Standard Update (Git + pip)

```bash
cd /path/to/engram_translator
git pull origin main
pip install -r requirements.txt
alembic upgrade head   # Apply any new database migrations
```

If you used the one-line installer, pull the latest code into the installation directory and the self-healing entry point will automatically detect and install new dependencies on the next launch.

### What Happens During an Update

1. **`git pull`** — Fetches the latest code from the `main` branch. This includes new features, bug fixes, ontology updates, and ML model improvements.
2. **`pip install -r requirements.txt`** — Picks up new or changed dependencies. Existing packages are skipped if they're already at the correct version.
3. **`alembic upgrade head`** — Applies database schema migrations. This is safe to run even if no migrations are pending — it's a no-op in that case.
4. **Self-healing entry point** — On the next launch via `./engram` or `.\engram.bat`, the entry point re-validates all imports and reinstalls if anything is missing.

### Post-Update Validation

```bash
engram info          # Verify configuration is intact
engram tools list    # Confirm tool registry is accessible
engram heal status   # Check for any new drifts after update
```

If `engram info` shows the correct API URL and authentication status, you're good. If `engram heal status` shows new drifts, this is expected — the update may have refined the ontology mappings. Review them or run `engram heal now` to auto-repair.

---

## Rollback

```bash
cd /path/to/engram_translator

# List recent commits
git log --oneline -10

# Roll back to a specific commit
git checkout <commit-hash>
pip install -r requirements.txt
alembic downgrade -1   # Revert the last migration if needed
```

> **Warning:** Rolling back database migrations can cause data loss if the newer migration added columns that already contain data. Always back up your database before downgrading:
> ```bash
> # PostgreSQL
> pg_dump translator_db > backup.sql
>
> # SQLite
> cp ./engram.db ./engram.db.backup
> ```

### Rollback Strategies

| Scenario | Strategy |
|---|---|
| Code bug (no schema changes) | `git checkout <hash>` — no migration needed |
| Bad migration | `alembic downgrade -1` + `git checkout <hash>` |
| Full reset | `git checkout <hash>` + restore database backup |

---

## Updating Docker Deployments

```bash
cd /path/to/engram_translator
git pull origin main
docker compose build app
docker compose up -d app   # Zero-downtime rolling restart
```

The `up -d` command only restarts services that have changed. Since the `app` image was rebuilt, only the gateway container restarts. Database and Redis continue running.

### Kubernetes

```bash
# Update the image tag
kubectl set image deployment/engram-gateway engram=engram:latest

# Watch the rollout
kubectl rollout status deployment/engram-gateway

# If something goes wrong, roll back
kubectl rollout undo deployment/engram-gateway
```

For production, use specific image tags (not `latest`) and update them in your manifests:

```yaml
spec:
  containers:
  - name: engram
    image: engram:v1.2.3  # Pin to specific version
```

---

## Uninstalling

### Remove the CLI

```bash
# Remove the global command
rm -f ~/bin/engram
rm -f ~/.local/bin/engram
```

### Remove the Codebase

```bash
rm -rf /path/to/engram_translator
```

### Remove Configuration and Data (Optional)

```bash
rm -rf ~/.engram
```

> **Note:** Keep `~/.engram/` if you plan to reinstall later. It contains your `config.yaml`, EAT tokens, encrypted credentials, and swarm memory database. Removing it is a full reset.

### Remove the Background Service

```bash
# Linux (systemd)
sudo systemctl stop engram && sudo systemctl disable engram
sudo rm /etc/systemd/system/engram.service
sudo systemctl daemon-reload

# macOS (launchd)
launchctl remove com.useengram.daemon
rm ~/Library/LaunchAgents/com.useengram.daemon.plist
```

### Remove Docker Resources

```bash
cd /path/to/engram_translator
docker compose down -v   # Stop all services and remove volumes
docker rmi engram:latest # Remove the image
```

### Remove the Keyring Entry

```bash
# Python
python -c "import keyring; keyring.delete_password('engram', 'eat_token')"
```

### Complete Uninstall Checklist

| Item | Command | What it removes |
|---|---|---|
| CLI wrapper | `rm ~/bin/engram` | The `engram` command |
| Codebase | `rm -rf /path/to/engram_translator` | All source code |
| Configuration | `rm -rf ~/.engram` | Config, tokens, swarm memory |
| Background service | `systemctl disable engram` | Auto-start daemon |
| Docker resources | `docker compose down -v` | Containers, volumes, networks |
| Keyring entry | `keyring.delete_password(...)` | Stored EAT token |

---

## What's Next

- **[Installation](./02-installation.md)** — Reinstall from scratch
- **[Docker & Kubernetes Setup](./03-docker-kubernetes.md)** — Deploy with containers
