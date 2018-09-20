#!/bin/sh

PYTHONPATH=src python2 src/feedmark/tests.py || exit 1
PYTHONPATH=src python3 src/feedmark/tests.py || exit 1
