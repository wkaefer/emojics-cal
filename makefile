MAKEFLAGS=-s --no-print-directory

.ONESHELL:
.DEFAULT: ; @:
.PHONY: help holidays jwk github-push targets

# ═══════════════════════════════════════════════════════════════════
# 📋  Misc
# ═══════════════════════════════════════════════════════════════════

help:
	@printf '%s\n' \
		'jwk             Add GitHub remote (run once)' \
		'holidays        Generate 2026 holiday scrapbook .ics files' \
		'github-push     Push orphan snapshot to GitHub main' \
		'targets         List make target names only'

#
# targets - List make target names only
# ----------------------------------------
targets:
	@printf '%s\n' github-push help holidays jwk targets

#
# holidays - Generate 2026 holiday scrapbook .ics files
# -----------------------------------------------------
holidays:
	python3 tools/generate-holiday-ics.py --year 2026

# 🌵🌵🌵🌵🌵🌵🌵🌵🌵🌵🌵🌵🌵🌵🌵🌵 jwk 🌵🌵🌵🌵🌵🌵🌵🌵🌵🌵🌵🌵🌵🌵🌵🌵

#
# jwk - Add GitHub remote (run once)
# ------------------------------------
jwk:
	git remote add github git@github.com:wkaefer/emojics-cal.git

# 🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀 github 🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀

#
# github-push - Push orphan snapshot to GitHub main
# --------------------------------------------------
github-push:
	git checkout --orphan github-staging
	git commit -m "Snapshot: $$(date +%Y-%m-%d)"
	git push --force github github-staging:main
	git checkout main
	git branch -D github-staging

# vim: set ft=make ts=8 sw=8 noet :
wes:
	python3 tools/generate-holiday-ics.py \
		--date 2026-07-07 \
		--title "Wes Birthday" \
		--description "Birthday Party Party with a green theme and giant cake"
