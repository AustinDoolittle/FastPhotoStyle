#!/usr/bin/env bash
FLASK_APP = app.py:app
FLASK_ENV = production
FLASK_DEBUG = 0
python -m flask run --host=0.0.0.0 --port=8888