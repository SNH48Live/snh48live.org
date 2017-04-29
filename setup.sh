#!/usr/bin/env zsh

print_progress () print -R $'\e[32m'"$*"$'\e[0m' >&2

here=$0:A:h

print_progress 'Setting up venv and requirements...'
[[ -d $here/venv ]] || /usr/bin/python3 -m venv $here/venv
$here/venv/bin/pip install -r $here/feed/requirements.txt -r $here/schedule/requirements.txt -r $here/stats/requirements.txt
