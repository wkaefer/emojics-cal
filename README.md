# emojics-cal 📅 #

A zero-dependency personal calendar scrapbook. Attach diary entries and photos
to any date, with emoji-themed decorations for each month. Runs entirely in the
browser using IndexedDB for persistence, with an optional Apache/CGI backend for
syncing events as `.ics` files.

## Features ✨ ##

- 🗓️ Monthly calendar view with previous/next navigation and a Today button
- 📝 Per-date modal — title, freeform description, and multiple photo attachments
- 🖼️ Photos resized on upload and displayed as a stacked thumbnail pile per day
- 🔎 Full lightbox gallery with arrow and keyboard navigation
- 🖨️ Print preview — styled letter-size layout with photo grid and color/B&W toggle
- 📥 ICS import and export (RFC 5545, inline Base64 image attachments)
- 🗂️ Server ICS browser — list, fetch, and import `.ics` files stored on the server
- ⚖️ Conflict resolution on import — merge, overwrite, or skip per event
- ↩️ Undo on event and image deletion (6-second toast window)
- 🎨 Monthly emoji themes — each month gets a distinct gradient and four corner emoji
- 📖 Scrapbook view — collage popup with date-seeded colors, random decorative borders (torn, scalloped, deckle, polaroid, framed), and washi-tape accents; click any photo to open it in the gallery
- 🌐 URL-backed images — attach images by URL; lazy-fetched at display time, 🖼️ emoji fallback if unreachable; exported as `ATTACH;VALUE=URI` in ICS
- 🪶 No build step, no npm, no external libraries

## Setup 🛠️ ##

Drop all files into a web-accessible directory on an Apache server with CGI
enabled. The `.cgi` scripts must be executable:

```sh
chmod +x ics-get.cgi ics-list.cgi ics-put.cgi
```

The `.ics/` directory stores uploaded calendar files server-side. Apache must
have write permission to it for `ics-put.cgi` to work.

> 🚧 A live test site will be linked here once available.

## Holiday ICS Generator 🎆 ##

Generate scrapbook-style holiday `.ics` files with inline PNG attachments:

```sh
python3 tools/generate-holiday-ics.py --year 2026
```

The generator calls `josie /d3` for each holiday image, writes source and resized
PNGs into `.images/`, resizes embedded images to the app's `300x200` limit, and
writes the resulting calendar files into `.ics/`. To test the ICS writer without
calling the image API, run:

```sh
python3 tools/generate-holiday-ics.py --year 2026 --no-generate-images
```

Generate a single custom event by passing a date, title, and description. The
description is used for both the calendar event text and the generated image
prompt:

```sh
python3 tools/generate-holiday-ics.py \
  --date 2026-05-05 \
  --title "Bad Tamala Day" \
  --description "small scrapbook image of a dramatic tamale mishap, handmade paper collage style"
```

The same command is available as:

```sh
make holidays
```

## Keyboard Shortcuts ⌨️ ##

| Key         | Action                          |
|-------------|---------------------------------|
| `←` / `→`   | Previous / next month           |
| `↑` / `↓`   | Previous / next year            |
| `T`         | Jump to today                   |
| `←` / `→`   | Previous / next photo (gallery) |
| `Esc`       | Close gallery or modal          |

## Files 📁 ##

| File                 | 🧿 | Description                                     |
|----------------------|----|-------------------------------------------------|
| ics-get.cgi          | 🔩 | Serve a single .ics file by name                |
| ics-list.cgi         | 🔩 | List stored .ics files as JSON                  |
| ics-put.cgi          | 🔩 | Receive and save an uploaded .ics file          |
| index.html           | 🌐 | The entire application — SPA, zero dependencies |
| makefile             | 🚂 | GitHub push and dev workflow targets            |
| .ics/                | 📁 | Server-side ICS file storage (not indexed)      |

[# vim: set ft=markdown ts=2 sw=2 sts=2 et : ]: #

## Files ##

| File                 | 🧿 | Description                                     |
|----------------------|----|-------------------------------------------------|
| ics-get.cgi          | 🔩 | Serve a single .ics file by name                |
| ics-list.cgi         | 🔩 | List stored .ics files as JSON                  |
| ics-put.cgi          | 🔩 | Receive and save an uploaded .ics file          |
| index.html           | 🌐 | The entire application — SPA, zero dependencies |
| makefile             | 🚂 | GitHub push and dev workflow targets            |
| .ics/                | 📁 | Server-side ICS file storage (not indexed)      |
