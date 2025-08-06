#!/bin/bash

source .venv/bin/activate && python3 app.py && cd ./app/docker/ && docker-compose build --no-cache && docker-compose up 
