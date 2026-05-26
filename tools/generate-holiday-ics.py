#!/usr/bin/env python3
"""Generate scrapbook holiday .ics files with Josie-created image attachments."""

from __future__ import annotations

import argparse
import base64
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from PIL import Image


DEFAULT_YEAR = 2027
DEFAULT_IMAGE_SIZE = (300, 200)
CURRENT_PLAN_CUTOFF = date(2028, 1, 2)
DEFAULT_IMAGE_WAIT_SECONDS = 15 * 60
IMAGE_POLL_SECONDS = 5


@dataclass(frozen=True)
class Holiday:
    key: str
    title: str
    summary: str
    description: str
    prompt: str
    day: date

    @property
    def safe_title(self) -> str:
        safe = re.sub(r"[^A-Za-z0-9_-]+", "_", self.title).strip("_")
        return safe[:40] or "event"

    @property
    def filename(self) -> str:
        return f"{self.day.isoformat()}-{self.safe_title}.ics"

    @property
    def image_name(self) -> str:
        return f"{self.day.isoformat()}-{self.safe_title}.png"


def nth_weekday(year: int, month: int, weekday: int, nth: int) -> date:
    """Return nth weekday in month, where Monday is 0."""
    d = date(year, month, 1)
    d += timedelta(days=(weekday - d.weekday()) % 7)
    return d + timedelta(days=7 * (nth - 1))


def last_weekday(year: int, month: int, weekday: int) -> date:
    """Return last weekday in month, where Monday is 0."""
    if month == 12:
        d = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        d = date(year, month + 1, 1) - timedelta(days=1)
    return d - timedelta(days=(d.weekday() - weekday) % 7)


def easter_date(year: int) -> date:
    """Return Western Easter Sunday for the Gregorian calendar."""
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return date(year, month, day)


def holiday_specs(year: int) -> list[Holiday]:
    specs = [
        (
            "new-years-day",
            "New Year's Day",
            "New Year's Day 🎉",
            "Placeholder scrapbook page for New Year's Day.",
            "small scrapbook placeholder image for New Year's Day, confetti, champagne sparkle, fresh calendar page, paper collage style",
            date(year, 1, 1),
        ),
        (
            "mlk-day",
            "Martin Luther King Jr. Day",
            "Martin Luther King Jr. Day 🕊️",
            "Placeholder scrapbook page for Martin Luther King Jr. Day.",
            "small scrapbook placeholder image for Martin Luther King Jr. Day, peaceful dove, warm light, civic remembrance, paper collage style",
            nth_weekday(year, 1, 0, 3),
        ),
        (
            "valentines-day",
            "Valentine's Day",
            "Valentine's Day 💘",
            "Placeholder scrapbook page for Valentine's Day.",
            "small scrapbook placeholder image for Valentine's Day, layered paper hearts, pink red accents, handmade scrapbook style",
            date(year, 2, 14),
        ),
        (
            "presidents-day",
            "Presidents' Day",
            "Presidents' Day 🇺🇸",
            "Placeholder scrapbook page for Presidents' Day.",
            "small scrapbook placeholder image for Presidents' Day, stars and stripes, classic civic holiday, paper collage style",
            nth_weekday(year, 2, 0, 3),
        ),
        (
            "st-patricks-day",
            "St. Patrick's Day",
            "St. Patrick's Day ☘️",
            "Placeholder scrapbook page for St. Patrick's Day.",
            "small scrapbook placeholder image for St. Patrick's Day, shamrocks, green ribbon, gold accents, paper collage style",
            date(year, 3, 17),
        ),
        (
            "easter",
            "Easter",
            "Easter 🐣",
            "Placeholder scrapbook page for Easter.",
            "small scrapbook placeholder image for Easter, decorated eggs, spring flowers, soft pastel paper collage",
            easter_date(year),
        ),
        (
            "mothers-day",
            "Mother's Day",
            "Mother's Day 💐",
            "Placeholder scrapbook page for Mother's Day.",
            "small scrapbook placeholder image for Mother's Day, bouquet, handwritten card, warm floral scrapbook style",
            nth_weekday(year, 5, 6, 2),
        ),
        (
            "memorial-day",
            "Memorial Day",
            "Memorial Day 🇺🇸",
            "Placeholder scrapbook page for Memorial Day.",
            "small scrapbook placeholder image for Memorial Day, remembrance, folded flag, soft stars, warm paper texture",
            last_weekday(year, 5, 0),
        ),
        (
            "fathers-day",
            "Father's Day",
            "Father's Day 👔",
            "Placeholder scrapbook page for Father's Day.",
            "small scrapbook placeholder image for Father's Day, tie, handmade card, warm family scrapbook style",
            nth_weekday(year, 6, 6, 3),
        ),
        (
            "juneteenth",
            "Juneteenth",
            "Juneteenth ❤️💚💛",
            "Placeholder scrapbook page for Juneteenth.",
            "small scrapbook placeholder image for Juneteenth, red green yellow celebration, starburst, paper collage style",
            date(year, 6, 19),
        ),
        (
            "independence-day",
            "Independence Day",
            "Independence Day 🇺🇸",
            "Placeholder scrapbook page for Independence Day.",
            "small scrapbook placeholder image for July 4th Independence Day, fireworks, red white blue, festive paper collage",
            date(year, 7, 4),
        ),
        (
            "labor-day",
            "Labor Day",
            "Labor Day 🛠️",
            "Placeholder scrapbook page for Labor Day.",
            "small scrapbook placeholder image for Labor Day, simple tools, sunlit long weekend, paper scrapbook style",
            nth_weekday(year, 9, 0, 1),
        ),
        (
            "halloween",
            "Halloween",
            "Halloween 🎃",
            "Placeholder scrapbook page for Halloween.",
            "small scrapbook placeholder image for Halloween, friendly pumpkin, moon, playful spooky paper collage",
            date(year, 10, 31),
        ),
        (
            "veterans-day",
            "Veterans Day",
            "Veterans Day 🇺🇸",
            "Placeholder scrapbook page for Veterans Day.",
            "small scrapbook placeholder image for Veterans Day, flag colors, stars, respectful remembrance, scrapbook style",
            date(year, 11, 11),
        ),
        (
            "thanksgiving",
            "Thanksgiving",
            "Thanksgiving 🦃",
            "Placeholder scrapbook page for Thanksgiving.",
            "small scrapbook placeholder image for Thanksgiving, harvest table, autumn leaves, warm paper collage",
            nth_weekday(year, 11, 3, 4),
        ),
        (
            "christmas",
            "Christmas",
            "Christmas 🎄",
            "Placeholder scrapbook page for Christmas.",
            "small scrapbook placeholder image for Christmas, tree, star, gift wrap, cozy paper collage",
            date(year, 12, 25),
        ),
        (
            "new-years-eve",
            "New Year's Eve",
            "New Year's Eve 🥂",
            "Placeholder scrapbook page for New Year's Eve.",
            "small scrapbook placeholder image for New Year's Eve, midnight clock, confetti, party lights, paper collage style",
            date(year, 12, 31),
        ),
    ]
    return sorted((Holiday(*spec) for spec in specs), key=lambda holiday: holiday.day)


def selected_holidays(year: int, include_past: bool) -> list[Holiday]:
    holidays = holiday_specs(year)
    if include_past:
        return holidays
    if year == CURRENT_PLAN_CUTOFF.year:
        return [h for h in holidays if h.day >= CURRENT_PLAN_CUTOFF]
    return holidays


def parse_event_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("date must use YYYY-MM-DD format") from exc


def custom_holiday(day: date, title: str, description: str) -> Holiday:
    return Holiday(
        key="custom",
        title=title,
        summary=title,
        description=description,
        prompt=description,
        day=day,
    )


def ics_escape(value: str) -> str:
    return (
        str(value)
        .replace("\\", "\\\\")
        .replace("\r\n", "\\n")
        .replace("\r", "\\n")
        .replace("\n", "\\n")
        .replace(",", "\\,")
        .replace(";", "\\;")
    )


def ics_fold(line: str) -> str:
    raw = line.encode("utf-8")
    if len(raw) <= 75:
        return line
    out: list[str] = []
    buf = ""
    first = True
    buf_bytes = 0
    for ch in line:
        ch_len = len(ch.encode("utf-8"))
        limit = 75 if first else 74
        if buf_bytes + ch_len > limit:
            out.append(("" if first else " ") + buf)
            first = False
            buf = ch
            buf_bytes = ch_len
        else:
            buf += ch
            buf_bytes += ch_len
    if buf:
        out.append(("" if first else " ") + buf)
    return "\r\n".join(out)


def now_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def create_fallback_image(path: Path, title: str) -> None:
    """Create a simple PNG so --no-generate-images can bootstrap test output."""
    path.parent.mkdir(parents=True, exist_ok=True)
    img = Image.new("RGB", DEFAULT_IMAGE_SIZE, (246, 240, 229))
    # Keep this dependency-free beyond Pillow: draw simple colored bands only.
    pixels = img.load()
    bands = [(167, 45, 45), (238, 196, 91), (61, 117, 86), (48, 80, 125)]
    for y in range(DEFAULT_IMAGE_SIZE[1]):
        color = bands[(y // 50) % len(bands)]
        for x in range(DEFAULT_IMAGE_SIZE[0]):
            if 16 <= x <= DEFAULT_IMAGE_SIZE[0] - 16 and 16 <= y <= DEFAULT_IMAGE_SIZE[1] - 16:
                pixels[x, y] = color if (x + y) % 19 < 2 else (246, 240, 229)
    img.save(path, format="PNG", optimize=True)


def newest_png(images_dir: Path, before: set[Path]) -> Path | None:
    candidates = [p for p in images_dir.glob("*.png") if p not in before and p.is_file()]
    if not candidates:
        return None
    return max(candidates, key=lambda p: p.stat().st_mtime)


def wait_for_png(path: Path, timeout_seconds: int) -> bool:
    deadline = datetime.now() + timedelta(seconds=timeout_seconds)
    while datetime.now() <= deadline:
        if path.exists() and path.stat().st_size > 0:
            return True
        time.sleep(IMAGE_POLL_SECONDS)
    return False


def wait_for_newest_png(images_dir: Path, before: set[Path], timeout_seconds: int) -> Path | None:
    deadline = datetime.now() + timedelta(seconds=timeout_seconds)
    while datetime.now() <= deadline:
        found = newest_png(images_dir, before)
        if found and found.stat().st_size > 0:
            return found
        time.sleep(IMAGE_POLL_SECONDS)
    return None


def run_josie_image(prompt: str, images_dir: Path, josie_cmd: str, wait_seconds: int) -> Path:
    images_dir.mkdir(parents=True, exist_ok=True)
    before = set(images_dir.glob("*.png"))
    env = os.environ.copy()
    env["OUTPUT_IMAGES"] = str(images_dir)
    env.setdefault("JOSIE_IMAGE", "none")
    cmd = [josie_cmd, "/d3", prompt]
    result = subprocess.run(cmd, cwd=Path.cwd(), env=env, text=True, capture_output=True)
    combined = result.stdout + "\n" + result.stderr
    if result.returncode != 0 or "[error generating" in combined:
        sys.stderr.write(result.stdout)
        sys.stderr.write(result.stderr)
        raise RuntimeError(f"Josie image generation failed for prompt: {prompt}")

    match = re.search(r"saved to\s+([^\s]+\.png)", combined)
    if match:
        found = Path(match.group(1)).expanduser()
        if not found.is_absolute():
            found = Path.cwd() / found
        if wait_for_png(found, wait_seconds):
            return found

    found = wait_for_newest_png(images_dir, before, wait_seconds)
    if found:
        return found
    sys.stderr.write(result.stdout)
    sys.stderr.write(result.stderr)
    raise RuntimeError("Josie completed but no new PNG was found in the image directory")


def resize_png(source: Path, target: Path, max_size: tuple[int, int]) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(source) as img:
        img = img.convert("RGBA")
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        save_target = target
        if source.resolve() == target.resolve():
            save_target = target.with_suffix(".tmp.png")
        img.save(save_target, format="PNG", optimize=True)
        if save_target != target:
            save_target.replace(target)


def build_ics(holiday: Holiday, image_path: Path) -> str:
    b64 = base64.b64encode(image_path.read_bytes()).decode("ascii")
    dtstart = holiday.day.strftime("%Y%m%d")
    dtend = (holiday.day + timedelta(days=1)).strftime("%Y%m%d")
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//CalendarScrapbook//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "BEGIN:VEVENT",
        f"UID:scrapbook-{holiday.day.isoformat()}@local",
        f"DTSTAMP:{now_stamp()}",
        f"DTSTART;VALUE=DATE:{dtstart}",
        f"DTEND;VALUE=DATE:{dtend}",
        f"SUMMARY:{ics_escape(holiday.summary)}",
        f"DESCRIPTION:{ics_escape(holiday.description)}",
        f"ATTACH;FMTTYPE=image/png;ENCODING=BASE64;VALUE=BINARY:{b64}",
        "END:VEVENT",
        "END:VCALENDAR",
    ]
    return "\r\n".join(ics_fold(line) for line in lines) + "\r\n"


def write_holiday(
    holiday: Holiday,
    out_dir: Path,
    images_dir: Path,
    max_size: tuple[int, int],
    josie_cmd: str,
    image_wait_seconds: int,
    generate_images: bool,
    skip_existing: bool,
) -> Path | None:
    out_path = out_dir / holiday.filename
    resized_path = images_dir / holiday.image_name
    if skip_existing and out_path.exists():
        print(f"skip existing {out_path}")
        return None

    if generate_images:
        source = run_josie_image(holiday.prompt, images_dir, josie_cmd, image_wait_seconds)
        resize_png(source, resized_path, max_size)
    elif not resized_path.exists():
        create_fallback_image(resized_path, holiday.title)
    elif resized_path.exists():
        resize_png(resized_path, resized_path, max_size)

    out_dir.mkdir(parents=True, exist_ok=True)
    out_path.write_text(build_ics(holiday, resized_path), encoding="utf-8", newline="")
    print(f"wrote {out_path}")
    return out_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate scrapbook holiday .ics files with embedded PNG attachments."
    )
    parser.add_argument("--year", type=int, default=DEFAULT_YEAR)
    parser.add_argument("--date", type=parse_event_date, help="Custom event date in YYYY-MM-DD format")
    parser.add_argument("--title", help="Custom event title")
    parser.add_argument(
        "--description",
        help="Custom event description. In custom mode this is also used as the image prompt.",
    )
    parser.add_argument("--out", type=Path, default=Path(".ics"))
    parser.add_argument("--images", type=Path, default=Path(".images"))
    parser.add_argument("--josie", default="josie", help="Josie command to run")
    parser.add_argument(
        "--image-wait-seconds",
        type=int,
        default=DEFAULT_IMAGE_WAIT_SECONDS,
        help="Seconds to wait for josie /d3 to finish writing a PNG into .images.",
    )
    parser.add_argument("--max-width", type=int, default=DEFAULT_IMAGE_SIZE[0])
    parser.add_argument("--max-height", type=int, default=DEFAULT_IMAGE_SIZE[1])
    parser.add_argument("--include-past", action="store_true")
    parser.add_argument("--skip-existing", action="store_true")
    parser.add_argument(
        "--no-generate-images",
        action="store_true",
        help="Reuse existing resized images, creating simple fallback PNGs if missing.",
    )
    args = parser.parse_args()
    custom_fields = [args.date is not None, args.title is not None, args.description is not None]
    if any(custom_fields) and not all(custom_fields):
        parser.error("--date, --title, and --description must be passed together")
    return args


def main() -> int:
    args = parse_args()
    max_size = (args.max_width, args.max_height)
    events = (
        [custom_holiday(args.date, args.title, args.description)]
        if args.date and args.title and args.description
        else selected_holidays(args.year, args.include_past)
    )
    if not events:
        print(f"No holidays selected for {args.year}.")
        return 0

    for holiday in events:
        write_holiday(
            holiday=holiday,
            out_dir=args.out,
            images_dir=args.images,
            max_size=max_size,
            josie_cmd=args.josie,
            image_wait_seconds=args.image_wait_seconds,
            generate_images=not args.no_generate_images,
            skip_existing=args.skip_existing,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
