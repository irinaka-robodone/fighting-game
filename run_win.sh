#!bin/bash
$env:BASE_DIR = $(pwd)
mkdir -p asset/img
mkdir -p asset/sound
python -m pip install --upgrade pip
python -m venv .venv
.venv/Scripts/activate
pip install -r requirements.txt