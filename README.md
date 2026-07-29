# Event Guestbook

A mobile-focused photo feed for a single event.

Guests access the application through a shared QR code and can, depending on the current event phase, take photos, select images from their phone, upload multiple images at once, and browse the shared event feed.

The project is built with Django and is deployed as a separate instance for one event.

## Current Status

The backend domain model, lifecycle logic, access control, and basic multi-image upload flow are implemented.

The project currently includes:

* QR-based guest access
* Session-based access without user accounts
* Five event phases
* Declarative configuration for each phase
* Multiple images per upload
* Django Admin moderation
* Local filesystem-based media storage
* Tests for access, scheduling, configuration, models, forms, and views

The frontend is currently only a minimal working implementation.

The next step is to design the mobile interface and implement it with HTML, CSS, and JavaScript.

## Product Idea

The application is not intended to be a traditional guestbook with names and written messages.

Instead, it acts as a shared event album for candid party photos.

A guest should be able to:

1. Scan the event QR code.
2. Open the application without creating an account.
3. Take new photos or select existing images.
4. Upload multiple images together.
5. Browse photos uploaded by other guests.

## Architecture

The guestbook is controlled by two separate concepts:

1. **EventSchedule** determines which phase the event is currently in.
2. **PhaseConfiguration** determines which capabilities are available during that phase.

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

Time-based logic and feature rules are therefore kept separate.

`EventSchedule` only knows when a phase applies.

`PhaseConfiguration` only knows what is allowed during that phase.

## Event Phases

The event lifecycle consists of five phases:

```text
CLOSED → PRE → LIVE → POST → ARCHIVED
```

### CLOSED

The guestbook has not opened yet.

* The page is not accessible
* QR access is disabled
* Uploads are disabled
* The feed is hidden

### PRE

The guestbook is accessible before the event.

* QR access is allowed
* Uploads are disabled
* The feed is hidden

### LIVE

The event is currently taking place.

* QR access is allowed
* Image uploads are allowed
* Camera capture may be offered by the interface
* Multiple images may be uploaded together
* The feed is visible

### POST

The event has ended, but post-event uploads remain open.

* QR access is allowed
* Images may be selected from the device
* Multiple images may be uploaded together
* Direct camera capture is not shown
* The feed is visible

### ARCHIVED

The event is archived and read-only.

* QR access is allowed
* New uploads are disabled
* The feed remains visible

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

Templates and JavaScript use the same configuration to decide which interface elements to present, while the backend always enforces the rules independently.

## Schedule Model

Only the event start, event end, and two relative durations need to be configured:

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

## Data Model

A `Post` represents one upload action.

A post contains one or more images that were selected and uploaded together.

```text
Post
├── PostImage
├── PostImage
└── PostImage
```

`PostImage.position` preserves the order in which the images were submitted.

The application intentionally has no fields for:

* Usernames
* Written greetings
* Captions
* Comments
* Profiles

This keeps the upload flow fast and focused.

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

The session only identifies the current browser.

The current event phase and configuration then determine whether the page may be viewed and whether new images may be uploaded.

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
│   ├── lifecycle.py
│   ├── models.py
│   ├── phase_configuration.py
│   ├── phases.py
│   ├── posting.py
│   ├── schedule.py
│   ├── urls.py
│   ├── views.py
│   └── tests/
├── static/
├── templates/
├── Makefile
└── manage.py
```

### Module Responsibilities

`phases.py`
: Defines the possible event phases.

`schedule.py`
: Contains pure time-based calculations.

`phase_configuration.py`
: Contains the capabilities and rules for each phase.

`lifecycle.py`
: Connects Django settings and the system clock to the domain model.

`posting.py`
: Creates a post and its images inside a database transaction.

`access.py`
: Manages session-based guest access.

`views.py`
: Handles HTTP requests, rendering, redirects, and status codes.

## Local Installation

Create the virtual environment, install dependencies, and apply migrations:

```bash
make setup
```

Create a local `.env` file:

```dotenv
DEBUG=True
SECRET_KEY=django-insecure-local-development-key
GUESTBOOK_ACCESS_KEY=local-secret-key
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

Simulate a specific phase:

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
The complete test suite
```

## Tests

The test suite covers:

* Session-based guest access
* All phase boundaries
* Invalid schedule configurations
* Configuration for every phase
* Development phase overrides
* Models and image ordering
* QR access
* Index and upload permissions
* Valid and invalid image uploads
* Multiple images per post

Run:

```bash
make verify
```

## Media Storage

Local development currently uses Django's filesystem storage under:

```text
media/
```

Before production, persistent media storage should be moved to object storage.

The Django models use `ImageField`, which allows the storage implementation to be replaced through `STORAGES` without changing the domain model.

## Next Steps

1. Sketch mobile user flows and paper wireframes.
2. Create the visual design in Figma.
3. Implement the mobile interface with HTML, CSS, and JavaScript.
4. Test camera access, image selection, and multi-image uploads on real phones.
5. Configure persistent object storage.
6. Test the complete production flow through the final QR code.
7. Deploy and verify the event schedule configuration.

## Design Principles

The project prioritizes:

* Mobile-first usage
* Few and clear choices
* Fast uploads
* Declarative configuration
* Explicit module boundaries
* A small and understandable domain model
* Robust backend validation
* Minimal complexity
