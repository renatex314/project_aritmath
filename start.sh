#!/bin/bash
 
# Start both Python services in background
python /usr/src/app/main.py &
python /usr/src/app/api.py &

# Start nginx in foreground (keeps container alive)
nginx -g 'daemon off;'
