#!/usr/bin/env zsh

source /home/larsonmp/venv/default/bin/activate

python --version

#use one worker for now, the camera goes nuts with multiple workers
pushd src
exec gunicorn -b 0.0.0.0:10082 -w 1 service.rest.server:app

