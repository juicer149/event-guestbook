# Event Guestbook

A lightweight Django guestbook for a single event.

Each deployment hosts exactly one event. Event configuration lives in `config/settings.py`.

---

## Features

- QR-based guest access
- Session-based write permissions
- Public read access
- Multiple images per entry
- Four event phases
- Automatic archive after the event
- Django Admin moderation

---

## Project structure

```text
event-guestbook/
├── config/
│   ├── settings.py
│   └── urls.py
├── guestbook/
│   ├── access.py
│   ├── forms.py
│   ├── models.py
│   ├── phases.py
│   ├── urls.py
│   └── views.py
├── templates/
├── static/
└── manage.py
```

---

## Event configuration

Each deployment represents a single event.

The event is configured in `config/settings.py`.

```python
GUESTBOOK_TITLE
GUESTBOOK_STARTS_AT
GUESTBOOK_ENDS_AT
GUESTBOOK_CLOSES_AT
GUESTBOOK_ACCESS_KEY
```

---

## Event lifecycle

The guestbook automatically moves through four phases.

| Phase | Browse | Join | Create entries |
|-------|:------:|:----:|:--------------:|
| pre | ✓ | ✓ | ✗ |
| live | ✓ | ✓ | ✓ |
| post | ✓ | ✓ | ✓ |
| closed | ✓ | ✗ | ✗ |

The current phase is determined automatically from:

- `GUESTBOOK_STARTS_AT`
- `GUESTBOOK_ENDS_AT`
- `GUESTBOOK_CLOSES_AT`

---

## Guest access

Guests receive a QR code pointing to:

```text
/join/<access-key>/
```

A successful request grants write access for that browser by storing a session.

Write permissions are:

- stored in the browser session
- valid for 48 hours
- independent of the event phase

The access key is configured using:

```python
GUESTBOOK_ACCESS_KEY
```

Even with a valid session, new entries can only be created while the guestbook accepts submissions.

---

## Security model

- Anyone can browse the guestbook.
- Only guests with a valid QR link can create entries.
- Write permissions are stored in the browser session.
- Sessions expire automatically after 48 hours.
- The global event phase always overrides session permissions.

---

## Administration

Content is managed through Django Admin.

```text
/admin/
```

---

## Installation

Create a virtual environment and install the project.

```bash
python -m venv .venv
source .venv/bin/activate

make setup
```

---

## Local development

Start the development server.

```bash
make devrun
```

The default development access URL is:

```text
http://127.0.0.1:8000/join/local-secret-key/
```

### Simulating event phases

The current event phase can be overridden during development.

```bash
make devrun pre
make devrun live
make devrun post
make devrun closed
```

This override is only active while:

```python
DEBUG = True
```

Production always uses the configured event dates.

---

## Common commands

```bash
make setup
make migrate
make makemigrations

make devrun
make devrun pre
make devrun live
make devrun post
make devrun closed

make check
make test

make shell
make superuser
```

---

## Testing

Run Django system checks.

```bash
make check
```

Run the full test suite.

```bash
make test
```
