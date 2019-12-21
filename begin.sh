#!/bin/bash
set -e

virtualenv -p python3 venv || python3 -m venv venv || python -m venv venv
source venv/bin/activate || source venv/Scripts/activate
pip install --requirement requirements.txt
FLASK_APP=server.py flask run
