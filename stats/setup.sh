#!/usr/bin/env zsh

die () { echo -E "Error: $*" >&2; exit 1; }

user=${WWW_USER:-www-data}
group=${WWW_GROUP:-www-data}
here=$0:A:h
root=$here:h

[[ -f $here/client_secrets.json ]] || die 'client_secrets.json does not exist.'
if [[ -f $here/venv/bin/python ]]; then
    python=$here/venv/bin/python
elif [[ -f $root/venv/bin/python ]]; then
    python=$root/venv/bin/python
else
    die 'venv/bin/python does not exist.'
fi

dirs=(
    data
    logs
)
files=(
    analytics.sqlite3
    client_secrets.json
    credentials.json
)
for dir in $dirs; do
    sudo mkdir -p $here/$dir
    sudo chown $user:$group $here/$dir
    sudo chmod 750 $here/$dir
done
for file in $files; do
    sudo touch $here/$file
    sudo chown $user:$group $here/$file
    sudo chmod 640 $here/$file
done

sudo su $user -s /bin/sh -c "$python $here/update.py --authenticate --noauth_local_webserver"
