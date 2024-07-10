#!/bin/bash

profile=${1:?"Usage $0 <profile>"}

CONFIG_PATH=./data/$profile/config

# read project path from line 1
proj=$(sed -n '1p' $CONFIG_PATH)
server=./headless-lsp/src/lsp_server.py

cd $proj
cmake CMakeLists.txt
cd -

python $server --cwd=$proj --port=6256 --lsp-log=lsp.log --verbose
