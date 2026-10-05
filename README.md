# Event Guestbook

A QR-based shared photo album for a party, built with Django.

Guests scan a QR code, join without an account, upload photos from their
phone and browse everyone's pictures in one shared feed.

![Photo feed, upload page and selected photos](docs/screenshots/overview.png)

## Status

Built for a friend's 30th birthday in August 2026. Guests scanned a QR
code on the tables and uploaded 134 photos during the evening.

In October 2026 it was reused for a second party, an 18th birthday. Instead
of copying the code, everything that differs between two events was made
configurable: name, dates, theme, ornament and link preview. A new event is
now an `.env` file and, optionally, a theme file.

## Features

- Guest access through a shared join link (QR code) stored in the
  session, with no user accounts
- Five event phases (`closed`, `pre`, `live`, `post`, `archived`) driven
  by optional event dates and a declarative phase configuration
- Mobile upload with previews, removal, and separate gallery and camera
  actions
- Multiple images per upload, grouped as one post
- Originals stored without metadata (no GPS position), WebP thumbnails
  regeneratable from them
- Photo grid with a fullscreen lightbox (swipe, keyboard, loading
  feedback) and original download
- Themes as CSS variable files, with optional dark mode, divider ornament,
  favicon and link-preview image
- Link previews (Open Graph) for sharing in group chats
- Guest-friendly error pages in Swedish (400, 403, 404, 500)
- Moderation through Django Admin

## Demo

```bash
make setup
make demo
```

`make demo` resets the **local** database and media, creates 24
generated photos through the same upload path real guests use, and
starts the server in the LIVE phase. The browser opens automatically
when possible. Otherwise, open:

    http://127.0.0.1:8000/join/demo/

Opening `/` without joining returns 404 by design. After joining once,
the session keeps access.

Without `make`:

```bash
python manage.py migrate
python manage.py seed_demo
DEBUG=True GUESTBOOK_DEV_PHASE=live GUESTBOOK_ACCESS_KEY=demo \
  python manage.py runserver
```

## Setting up a new event

1. Copy `.env.example` to `.env` and set the event values below.
2. Pick a theme in `static/css/themes/`, or add one (see [Themes](#themes)).
3. Generate a long access key and print the join URL as a QR code:

   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(24))"
   ```

   The QR code points to `https://<your-domain>/join/<GUESTBOOK_ACCESS_KEY>/`.
   A new key per event means old QR codes stop working.
4. Deploy. `railway.json` runs `collectstatic`, `migrate` and gunicorn.
5. Before the party, open the QR link on a phone over mobile data, upload
   a photo, and check both light and dark mode.

The Makefile sources `.env` with the shell, so quote values that contain
spaces or `#`.

### Configuration

| Variable | Example | Purpose |
|---|---|---|
| `GUESTBOOK_TITLE` | `"Felicia 18"` | Heading, page title and link-preview title |
| `GUESTBOOK_EYEBROW` | `"24 OKTOBER"` | Small line above the title; empty hides it |
| `GUESTBOOK_DESCRIPTION` | `"Dela dina bilder från festen."` | Link-preview text |
| `GUESTBOOK_STARTS_AT` | `2026-10-24T18:00` | Event start, ISO 8601, Stockholm time unless an offset is given |
| `GUESTBOOK_ENDS_AT` | `2026-10-25T03:00` | Event end |
| `GUESTBOOK_THEME` | `felicia-18` | Loads `static/css/themes/<name>.css` |
| `GUESTBOOK_THEME_COLOR` | `"#fbf6f4"` | Browser UI color; match the theme's page background |
| `GUESTBOOK_THEME_COLOR_DARK` | `"#2a1d22"` | Same in dark mode, for themes that have one |
| `GUESTBOOK_ORNAMENT` | `bow` | Icon in the title divider from `static/img/ornaments/<name>.svg`; empty keeps a plain line |
| `GUESTBOOK_ACCESS_KEY` | | Secret part of the QR link |

Both dates are optional, and a missing date removes the phases on its side:

| Dates set | Phases |
|---|---|
| none | always `live` |
| start only | `closed` → `pre` → `live`, never closes |
| end only | `live` → `post` → `archived` |
| both | `closed` → `pre` → `live` → `post` → `archived` |

`pre` starts 10 days before the event and `post` lasts 24 hours after it.

Upload limits and development switches are documented in `.env.example`.
The app refuses to start with a missing theme or ornament, or an end date
before the start date.

### Themes

A theme is a CSS file in `static/css/themes/` that sets color variables on
`:root`. Layout and components live in `base.css` and only use these
variables:

| Variable | Used for |
|---|---|
| `--page-background`, `--surface` | Page and upload panel |
| `--text-primary`, `--text-secondary`, `--text-label` | Text |
| `--title-color` *(optional)* | Title and upload heading; falls back to `--text-primary` |
| `--gold` | Accent: divider, ornament, card borders, icons |
| `--button-background`, `--button-text` | Buttons |
| `--button-icon` *(optional)* | Icons in buttons; falls back to `--gold` |
| `--error` | Upload errors |
| `--placeholder`, `--disabled-*` | Image placeholder and disabled button |

`white-party.css` is the minimal example. `felicia-18.css` defines a palette
first and maps the variables onto it, and adds a dark mode by redefining the
same variables inside `@media (prefers-color-scheme: dark)`.

Optional files, used only when they exist:

| File | Use |
|---|---|
| `static/img/share/<theme>.png` | Link-preview image, 1200 × 630 |
| `static/img/favicons/<theme>.svg` | Favicon |
| `static/img/favicons/<theme>-32.png` | Favicon fallback |
| `static/img/favicons/<theme>-180.png` | iOS home screen icon |

Ornament SVGs are drawn as a CSS mask, so they take the theme's `--gold`
and need no color of their own.

## Development

```bash
make devrun live     # simulate a phase: closed, pre, live, post, archived
make test            # run the test suite
make verify          # system checks, migration check and tests
make help            # all commands
```

`make demo` always runs with `DEBUG=True`. To see the production error
pages locally, set `DEBUG=False` in `.env` and run `make collectstatic` and
`make run`.

## Design

| Module | Responsibility |
|---|---|
| `schedule.py` | Works out the current phase from the optional event dates (pure function) |
| `phase_configuration.py` | What each phase allows: joining, uploads, camera, feed |
| `lifecycle.py` | Connects schedule, configuration and settings |
| `access.py` | Grants and checks guest access in the session |
| `posting.py` | Creates a post and its images; removes stored files if the database step fails |
| `image_processing.py` | Metadata-free JPEG originals and orientation-aware WebP thumbnails |
| `themes.py`, `context_processors.py` | Resolve the theme, ornament and theme assets for every template |
| `checks.py` | Startup checks for theme, ornament and dates |
| `errors.py` | Error pages; fall back to plain text if rendering fails |
| `templatetags/guestbook_icons.py` | `{% icon "name" %}` renders SVGs from `templates/guestbook/icons/` inline |

Originals are re-encoded as JPEG on upload with EXIF orientation applied
and all metadata (including GPS position) removed, and stored under a
random file name. The originals are the source of truth. Thumbnails are
derived and can be rebuilt with `python manage.py rebuild_thumbnails`.

Link-preview tags live in `base.html`, so they are also on the 404 page a
preview crawler gets when it opens the QR link without a guest session.

## Known Limitations

Acceptable for a party among friends and family:

- No upload progress indicator
- Thumbnails are generated during the upload request
- Media files are served publicly by path (with unguessable names); only
  the pages require the join link
- The feed loads every image without pagination
- The feed crops every photo to the same shape rather than a masonry
  layout

## License

MIT
