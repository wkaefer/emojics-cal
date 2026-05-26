#!/bin/sh
# Save uploaded .ics content to ../.ics/<name>.
# CGI: PUT or POST. Filename comes from QUERY_STRING (?name=...).
# Body is the raw .ics text.
#
# Collision policy: if a file with the same name already exists AND
# its contents differ from the incoming body, save with an incrementing
# numeric extension: foo.ics → foo.1.ics → foo.2.ics → …

ICS_DIR="$(dirname "$0")/.ics"
mkdir -p "$ICS_DIR"

# Parse name from query string (very simple, expects ?name=foo.ics).
name=$(printf '%s' "$QUERY_STRING" | sed -n 's/^.*name=\([^&]*\).*$/\1/p')

# URL-decode (handle %20, %2D, etc.) — minimal decoder using printf.
decode() {
    printf '%b' "$(printf '%s' "$1" | sed 's/+/ /g; s/%/\\x/g')"
}
name=$(decode "$name")

# Sanitize: only allow [A-Za-z0-9._-], strip path components, force .ics suffix.
name=$(printf '%s' "$name" | tr -cd 'A-Za-z0-9._-')
case "$name" in
    *.ics) : ;;
    *)     name="${name}.ics" ;;
esac

if [ -z "$name" ] || [ "$name" = ".ics" ]; then
    printf 'Status: 400 Bad Request\r\n'
    printf 'Content-Type: text/plain\r\n\r\n'
    printf 'Missing or invalid name parameter.\n'
    exit 0
fi

# Read the incoming body into a temp file first so we can diff it.
tmp=$(mktemp)
if [ -n "$CONTENT_LENGTH" ] && [ "$CONTENT_LENGTH" -gt 0 ] 2>/dev/null; then
    head -c "$CONTENT_LENGTH" > "$tmp"
else
    cat > "$tmp"
fi

# Determine the actual save target.
# Strip the trailing .ics to get the base stem for numbered variants.
base="${name%.ics}"   # e.g. "mycal"
target="$ICS_DIR/$name"

if [ -f "$target" ] && ! cmp -s "$tmp" "$target"; then
    # Same filename, different contents — find the next free slot.
    n=1
    while [ -f "$ICS_DIR/${base}.${n}.ics" ]; do
        n=$((n + 1))
    done
    name="${base}.${n}.ics"
    target="$ICS_DIR/$name"
fi

cp "$tmp" "$target"
rm -f "$tmp"

bytes=$(stat -c %s "$target" 2>/dev/null || stat -f %z "$target")

printf 'Status: 200 OK\r\n'
printf 'Content-Type: application/json\r\n\r\n'
printf '{"ok":true,"name":"%s","bytes":%s}' "$name" "$bytes"
