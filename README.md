# Event Guestbook

A mobile-first photo feed for a single event.

Guests access the application through a shared QR code and can,
depending on the current event phase, select photos from their phone,
upload multiple images at once, and browse the shared event album.

The project is built with Django and is intended to be deployed as a
separate instance for one event.

## Current Status

The backend domain model, lifecycle logic, access control, multi-image
upload flow, thumbnail generation, and the first mobile feed interface
are implemented.

The project currently includes:

- QR-based guest access
- Session-based access without user accounts
- Five event lifecycle phases
- Declarative configuration for each phase
- Multiple images per upload
- Automatic WebP thumbnail generation
- A thumbnail-based mobile masonry feed
- Regeneratable thumbnails derived from stored originals
- Django Admin moderation
- Local filesystem-based media storage
- Automated tests for access, scheduling, configuration, models,
  forms, image processing, posting, and views

The main feed has an initial mobile-first visual design.

The upload selection interface, client-side image previews, upload
progress, confirmation state, and fullscreen image viewer still require
frontend work.

## Product Idea

The application is not intended to be a traditional guestbook with
names and written messages.

Instead, it acts as a shared event album for candid party photos.

A guest should be able to:

1. Scan the event QR code.
2. Open the application without creating an account.
3. Take new photos or select existing images.
4. Upload multiple images together.
5. Browse photos uploaded by other guests.

The application deliberately avoids social-network features such as
profiles, likes, comments, captions, and follower relationships.

The goal is a fast and focused event experience.

## Architecture

The guestbook lifecycle is controlled by two separate concepts:

1. `EventSchedule` determines which phase the event is currently in.
2. `PhaseConfiguration` determines which capabilities are available
   during that phase.

```text
Current time
     │
     ▼
EventSchedule
     │
     ▼
GuestbookPhase
     │
     ▼
PhaseConfiguration lookup
     │
     ▼
Views / Templates / JavaScript
```

Time-based logic and feature rules are kept separate.

`EventSchedule` only knows when a phase applies.

`PhaseConfiguration` only knows what is allowed during that phase.

This prevents event rules from being duplicated across views and
templates.

## Event Phases

The event lifecycle consists of five phases:

```text
CLOSED → PRE → LIVE → POST → ARCHIVED
```

### CLOSED

The guestbook has not opened yet.

- The page is not accessible
- QR access is disabled
- Uploads are disabled
- The feed is hidden

### PRE

The guestbook is accessible before the event.

- QR access is allowed
- Uploads are disabled
- The feed is hidden
- A pre-event message may be shown

### LIVE

The event is currently taking place.

- QR access is allowed
- Image uploads are allowed
- Camera capture may be offered by the interface
- Multiple images may be uploaded together
- The feed is visible

### POST

The event has ended, but post-event uploads remain open.

- QR access is allowed
- Existing images may be selected from the device
- Multiple images may be uploaded together
- Direct camera capture is hidden
- The feed is visible

### ARCHIVED

The event is archived and read-only.

- QR access is allowed
- New uploads are disabled
- The feed remains visible

## Phase Configuration

The phase rules are represented as a declarative lookup table.

```python
PHASE_CONFIGURATIONS = {
    GuestbookPhase.CLOSED: ...,
    GuestbookPhase.PRE: ...,
    GuestbookPhase.LIVE: ...,
    GuestbookPhase.POST: ...,
    GuestbookPhase.ARCHIVED: ...,
}
```

The current application state is resolved with:

```python
phase = schedule.phase_at(moment)
configuration = configuration_for(phase)
```

Views therefore do not need long chains of phase-specific conditions.

Templates use the resolved configuration to decide which interface
elements should be displayed, while the backend always enforces the
rules independently.

For example:

```text
PhaseConfiguration
    decides whether uploads are allowed

View
    enforces the upload permission

Template
    shows or hides the upload control
```

## Schedule Model

Only the event start, event end, and two relative durations need to be
configured:

```python
GUESTBOOK_STARTS_AT
GUESTBOOK_ENDS_AT
GUESTBOOK_PRE_DURATION
GUESTBOOK_POST_DURATION
```

The remaining boundaries are derived automatically:

```text
PRE_START = EVENT_START - PRE_DURATION
POST_END  = EVENT_END + POST_DURATION
```

The phases use left-inclusive and right-exclusive intervals:

```text
CLOSED     moment < PRE_START

PRE        PRE_START <= moment < EVENT_START

LIVE       EVENT_START <= moment < EVENT_END

POST       EVENT_END <= moment < POST_END

ARCHIVED   POST_END <= moment
```

The schedule uses timezone-aware datetimes.

## Data Model

A `Post` represents one upload action.

It groups one or more images that were selected and uploaded together,
but the group is not presented as a visible post in the public feed.

```text
Post
├── PostImage
├── PostImage
└── PostImage
```

Each `PostImage` contains:

- The stored original image
- A generated WebP thumbnail
- Its creation timestamp
- A reference to the upload group

The original image is the permanent source of truth.

The thumbnail is a derived asset and may be regenerated from the
original if it is missing or if the thumbnail rules change.

The feed queries and renders `PostImage` objects directly, ordered
newest first.

```text
Newest PostImage
        ↓
Older PostImage
        ↓
Older PostImage
```

The application intentionally has no fields for:

- Usernames
- Written greetings
- Captions
- Comments
- Likes
- Profiles

This keeps the upload flow fast and focused.

## Image Processing

Uploaded images pass through a small image-processing pipeline.

```text
Uploaded image
      │
      ├── Stored original
      │
      └── Generated WebP thumbnail
```

The original image is preserved.

The thumbnail:

- Uses WebP
- Preserves the original aspect ratio
- Fits within a configured maximum size
- Is used in the public feed
- Can be rebuilt from the original

The thumbnail process also applies EXIF orientation before generating
the derived image. This is important for mobile photos, where the
visual orientation may be stored as metadata rather than reflected in
the raw pixel dimensions.

The feed therefore uses:

```text
Thumbnail
    fast feed rendering

Original
    fullscreen or detailed viewing
```

The image layout is handled by the frontend. No masonry position,
orientation category, width, height, or aspect-ratio value is stored in
the database.

## Guest Access

Guests do not create user accounts.

Each event uses a shared QR link:

```text
/join/<access-key>/
```

When the link is opened:

1. The access key is compared with the configured server value.
2. Guest access is stored in the browser's Django session.
3. The guest is redirected to the photo feed.

The session identifies only the current browser.

The current event phase and configuration then determine whether the
page may be viewed and whether new images may be uploaded.

The event owner manages content through Django Admin.

## Project Structure

```text
event-guestbook/
├── config/
│   ├── settings.py
│   └── urls.py
├── guestbook/
│   ├── access.py
│   ├── admin.py
│   ├── forms.py
│   ├── image_processing.py
│   ├── lifecycle.py
│   ├── management/
│   │   └── commands/
│   │       └── rebuild_thumbnails.py
│   ├── migrations/
│   ├── models.py
│   ├── phase_configuration.py
│   ├── phases.py
│   ├── posting.py
│   ├── schedule.py
│   ├── urls.py
│   ├── views.py
│   └── tests/
├── static/
│   └── css/
│       ├── base.css
│       └── white-party.css
├── templates/
│   ├── base.html
│   └── guestbook/
│       ├── index.html
│       └── upload_photos.html
├── Makefile
├── README.md
└── manage.py
```

## Module Responsibilities

`phases.py`
: Defines the possible event phases.

`schedule.py`
: Contains pure time-based calculations.

`phase_configuration.py`
: Contains the capabilities and rules for each phase.

`lifecycle.py`
: Connects Django settings and the system clock to the domain model.

`image_processing.py`
: Creates proportion-preserving WebP thumbnails from uploaded images.

`posting.py`
: Stores original images, generates thumbnails, and creates the
database records for one upload action.

`rebuild_thumbnails.py`
: Regenerates derived thumbnails from stored original images.

`access.py`
: Manages session-based guest access.

`forms.py`
: Validates uploaded files, image counts, and file-size limits.

`views.py`
: Handles HTTP requests, permissions, rendering, redirects, and status
codes.

`models.py`
: Defines upload groups and persisted event images.

## Local Installation

Create the virtual environment, install dependencies, and apply
migrations:

```bash
make setup
```

Create a local `.env` file:

```dotenv
DEBUG=True
SECRET_KEY=django-insecure-local-development-key
GUESTBOOK_ACCESS_KEY=local-secret-key
GUESTBOOK_TITLE=White Party
```

The `.env` file must not be committed.

```gitignore
.env
```

## Local Development

Start the server using the configured event dates:

```bash
make run
```

Simulate a specific lifecycle phase:

```bash
make devrun closed
make devrun pre
make devrun live
make devrun post
make devrun archived
```

Open the local QR access link:

```text
http://127.0.0.1:8000/join/local-secret-key/
```

The environment file is loaded by the Makefile when it exists.

## Common Commands

```bash
make check
make test
make verify

make makemigrations
make migrate
make showmigrations

make superuser
make shell
make collectstatic
```

`make verify` runs:

```text
Django system checks
Migration consistency checks
The complete automated test suite
```

## Upload Limits

Upload limits are configured through environment variables.

```dotenv
GUESTBOOK_MAX_IMAGES_PER_POST=20
GUESTBOOK_MAX_IMAGE_BYTES=15728640
GUESTBOOK_MAX_REQUEST_BYTES=262144000
```

The current defaults are:

```text
Maximum images per upload: 20
Maximum size per image:    15 MB
Maximum request size:      250 MB
```

The form validates image count and per-file size.

Django's request settings provide an additional outer request-size
boundary.

## Tests

The test suite currently contains 70 automated tests.

It covers:

- Session-based guest access
- QR join behaviour
- All phase boundaries
- Invalid schedule configurations
- Configuration for every phase
- Development phase overrides
- Models and upload grouping
- Image processing and thumbnail dimensions
- Original and thumbnail storage
- Thumbnail generation
- Index permissions
- Upload permissions
- Valid and invalid image uploads
- Multiple images per upload
- HTTP method restrictions

Run:

```bash
make verify
```

## Media Storage

Local development currently uses Django's filesystem storage under:

```text
media/
```

The current filesystem structure is approximately:

```text
media/
└── guestbook/
    ├── originals/
    │   └── YYYY/
    │       └── MM/
    │           └── DD/
    └── thumbnails/
        └── YYYY/
            └── MM/
                └── DD/
```

The original files are permanent source assets.

Thumbnails are replaceable derived assets.

Before production, persistent media storage should be configured. The
project currently supports a Railway volume through:

```text
RAILWAY_VOLUME_MOUNT_PATH
```

Object storage may later replace the filesystem storage backend.

The Django models use `ImageField`, which allows the storage
implementation to be replaced through `STORAGES` without changing the
domain model.

## Thumbnail Regeneration

Thumbnails can be regenerated from the stored original images at any
time.

Rebuild every thumbnail:

```bash
python manage.py rebuild_thumbnails
```

Rebuild only missing thumbnails:

```bash
python manage.py rebuild_thumbnails --missing-only
```

This means the important backup sources are:

```text
Original image files
Database records
```

Thumbnails do not need to be treated as irreplaceable data.

## Mobile Interface

The public feed is designed as a mobile-only or strongly mobile-first
experience.

The current feed includes:

- Event identity
- Image count
- A three-column masonry-style image layout
- Thumbnail-based image rendering
- A fixed bottom upload action
- Safe-area handling for mobile devices
- A narrow maximum page width for desktop development

The interface uses:

- Instrument Serif for the event title
- Inter for interface labels and controls
- Warm white surfaces
- Dark typography
- Restrained gold accents

The design is intended to match a White Party theme while allowing the
guest photos to remain the strongest visual element.

## Feed Ordering

Images are ordered newest first.

The default database ordering is:

```python
ordering = [
    "-created_at",
    "-id",
]
```

The primary ordering is the creation timestamp.

The primary key acts as a deterministic tie-breaker when multiple
images receive the same timestamp.

The masonry layout controls visual placement, while the database
controls the input order.

## Current Frontend Limitations

The feed interface is functional, but several interaction states remain
to be implemented:

- Client-side image previews before upload
- Removing selected images before upload
- Separate gallery and camera controls
- Upload progress feedback
- Upload success confirmation
- Upload failure feedback
- Fullscreen image viewing
- Swipe navigation between fullscreen images
- More complete empty and loading states

The current upload form remains intentionally simple so that the full
backend upload flow can be tested independently of the final frontend.

## Next Steps

1. Complete the mobile upload selection interface.
2. Add client-side image previews and removal controls.
3. Add gallery and camera actions.
4. Add upload progress and disabled submission states.
5. Add upload success and failure states.
6. Add fullscreen image viewing.
7. Test the complete flow on real iOS and Android devices.
8. Configure persistent production media storage.
9. Test the final QR access flow.
10. Deploy and verify the production event schedule.

## Design Principles

The project prioritizes:

- Mobile-first usage
- Few and clear choices
- Fast uploads
- Literal and understandable interface labels
- Declarative configuration
- Explicit module boundaries
- A small and understandable domain model
- Robust backend validation
- Replaceable derived assets
- Minimal complexity
- Clear separation between domain logic and presentation
