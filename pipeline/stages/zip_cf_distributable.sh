#!/usr/bin/env bash

# Zip final dist package without dist/ path included
cd dist
zip -qr ../task-runner-functions.zip .
cd ..