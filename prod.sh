#!/usr/bin/env sh

set -e

docker compose -f compose.yml up -d --build
