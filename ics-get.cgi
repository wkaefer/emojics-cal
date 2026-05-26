#!/bin/sh
# Stream a single .ics file from ../.ics by name.
# CGI: GET. ?name=foo.ics

ICS_DIR="$(dirname "$0")/.ics"

name=$(printf '%s' "$QUERY_STRING" | sed -n 's/^.*name=\([^&]*\).*$/\1/p')
decode() {
    printf '%b' "$(printf '%s' "$1" | sed 's/+/ /g; s/%/\\x/g')"
}
name=$(decode "$name")
name=$(printf '%s' "$name" | tr -cd 'A-Za-z0-9._-')

if [ -z "$name" ]; then
    printf 'Status: 400 Bad Request\r\n'
    printf 'Content-Type: text/plain\r\n\r\n'
    printf 'Missing name.\n'
    exit 0
fi

target="$ICS_DIR/$name"
if [ ! -f "$target" ]; then
    printf 'Status: 404 Not Found\r\n'
    printf 'Content-Type: text/plain\r\n\r\n'
    printf 'Not found: %s\n' "$name"
    exit 0
fi

printf 'Content-Type: text/calendar; charset=utf-8\r\n'
printf 'Content-Disposition: inline; filename="%s"\r\n' "$name"
printf 'Cache-Control: no-store\r\n'
printf '\r\n'
cat "$target"
