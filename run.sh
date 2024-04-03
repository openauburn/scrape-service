#!/bin/bash -x
# Run this script to start the development environment for scrape-service

PWD=`pwd`
activate () {
    . $PWD/.venv/bin/activate
    if [ "$1" == "prod" ]; then
        source .env.prod
    else
        source .env.dev
    fi
}

activate