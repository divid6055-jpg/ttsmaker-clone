# Deployment helpers

This directory contains drop-in templates for common deployment scenarios.
None of them are auto-applied — read them and adapt the paths/users/domains to your environment.

| File                  | Purpose                                              |
|-----------------------|------------------------------------------------------|
| `ttsmaker.service`    | systemd unit running gunicorn behind nginx           |
| `nginx.conf.example`  | nginx reverse proxy config (HTTP — add TLS via certbot) |

The repository root also contains:

- `Procfile` — for Heroku, Railway, Render, Fly.io, etc.
- `Dockerfile` — for any container platform.

See the project [README](../README.md) for the full step-by-step deployment walkthrough.
