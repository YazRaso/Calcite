#!/bin/bash

source .venv/bin/activate && cd ./app/docker/ && docker-compose build --no-cache && docker-compose up 
