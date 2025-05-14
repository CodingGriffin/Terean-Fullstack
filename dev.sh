#!/usr/bin/env sh

set -e

docker compose -f compose.yml -f compose.dev.yml up -d --build
