#!/usr/bin/env bash
export FLASK_APP=app.py:app
export FLASK_ENV=production
export FLASK_DEBUG=0
python -m flask run --host=0.0.0.0 --port=8888
