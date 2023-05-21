#!/bin/sh
docker build -t crm-django:v1 -f Dockerfile.local .
docker run --publish 8000:8000 crm-django:v1
