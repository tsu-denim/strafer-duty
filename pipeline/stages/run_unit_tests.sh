#!/usr/bin/env bash

sudo -H python3.6 -m pytest --test_resource_path="pipeline/unit_tests/test_resources/" ./pipeline/unit_tests/unit_tests_jasminFile.py
sudo -H python3.6 -m pytest --test_resource_path="pipeline/unit_tests/test_resources/" ./pipeline/unit_tests/unit_tests_jasminManifest.py
sudo -H python3.6 -m pytest --test_resource_path="pipeline/unit_tests/test_resources/" ./pipeline/unit_tests/unit_tests_jasminTest.py
