#!/bin/sh
# List .ics files in ../.ics as a JSON array.
# CGI: GET only.

ICS_DIR="$(dirname "$0")/.ics"

printf 'Content-Type: application/json\r\n'
printf 'Cache-Control: no-store\r\n'
printf '\r\n'

if [ ! -d "$ICS_DIR" ]; then
    printf '[]'
    exit 0
fi

# Build a JSON array of {name, size, mtime} for each .ics file.
first=1
printf '['
for f in "$ICS_DIR"/*.ics; do
    [ -e "$f" ] || continue
    name=$(basename "$f")
    size=$(stat -c %s "$f" 2>/dev/null || stat -f %z "$f")
    mtime=$(stat -c %Y "$f" 2>/dev/null || stat -f %m "$f")
    # Escape backslash and double quote in filename for JSON safety.
    esc_name=$(printf '%s' "$name" | sed 's/\\/\\\\/g; s/"/\\"/g')
    if [ $first -eq 1 ]; then
        first=0
    else
        printf ','
    fi
    printf '{"name":"%s","size":%s,"mtime":%s}' "$esc_name" "$size" "$mtime"
done
printf ']'
