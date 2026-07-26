# Event Guestbook

A lightweight Django guestbook for a single event.

Each deployment hosts exactly one event. The event is configured in
`config/settings.py`.

---

## Features

- QR-based guest access
- Browser session authentication
- Multiple images per entry
- Time-based event lifecycle
- Django Admin moderation
- Simple local development workflow

---

## Project structure

```text
event-guestbook/
├── config/
├── guestbook/
├── templates/
├── static/
├── Makefile
└── manage.py
```

---

## Event configuration

Each deployment represents a single event.

The required settings are:

```python
GUESTBOOK_TITLE
GUESTBOOK_STARTS_AT
GUESTBOOK_ENDS_AT
GUESTBOOK_ACCESS_KEY
```

Additional time windows are derived from the event:

```python
GUESTBOOK_JOIN_OPENS_AT
GUESTBOOK_JOIN_CLOSES_AT
GUESTBOOK_ENTRIES_CLOSE_AT
GUESTBOOK_CLOSES_AT
GUESTBOOK_GUEST_ACCESS_DURATION
```

This keeps only the important values configurable while everything else
follows automatically.

---

## Access model

Guests do not create accounts.

Instead, every invitation contains the same QR code:

```text
/join/<access-key>/
```

When a guest scans the QR code:

1. The access key is verified.
2. A Django session is created for that browser.
3. The browser is considered an approved guest until the session expires.

The session only identifies the browser.

Whether guests may currently read or create entries is determined by the
event lifecycle.

Event owners use Django Admin instead of guest sessions.

---

## Event lifecycle

The guestbook automatically moves through four phases.

| Phase | Read | Join | Create |
|------|:---:|:---:|:---:|
| pre | ✓ | ✓ | ✗ |
| live | ✓ | ✓ | ✓ |
| post | ✓ | ✓* | ✗ |
| closed | ✗ | ✗ | ✗ |

\* During development, `post` still allows testing the join flow. In production,
the actual join window is controlled by `GUESTBOOK_JOIN_CLOSES_AT`.

---

## Environment variables

Production:

```text
SECRET_KEY
DEBUG=False
GUESTBOOK_ACCESS_KEY
```

Development:

```bash
make devrun
```

The Makefile automatically provides a local access key.

---

## Local development

Run using the configured event dates:

```bash
make devrun
```

Or simulate any phase:

```bash
make devrun pre
make devrun live
make devrun post
make devrun closed
```

The development override only works while:

```python
DEBUG = True
```

---

## Administration

Owners manage the guestbook through Django Admin.

```text
/admin/
```

Create an administrator:

```bash
make superuser
```

---

## Common commands

```bash
make setup

make devrun
make devrun pre
make devrun live
make devrun post
make devrun closed

make check
make test
```

---

## Deployment

1. Deploy to Railway.
2. Configure the production environment variables.
3. Run migrations.
4. Configure persistent media storage.
5. Generate the final QR code using:

```text
https://<domain>/join/<access-key>/
```

The QR code should only be generated after the production domain and access
key have been finalized.
