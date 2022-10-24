#!/bin/bash
export FLASK_APP="/app/server"
export FLASK_ENV="development" # <- change to production

flask run --host=0.0.0.0 --port=8080
