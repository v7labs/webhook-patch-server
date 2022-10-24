#!/bin/bash
export FLASK_APP="/app/server"
export FLASK_ENV="production" # <- should be production # for debug: development
#export FLASK_DEBUG=1

flask --debug run --host=0.0.0.0 --port=8080 > "/app/log/log.txt" 