#!/bin/bash

. "./env/bin/activate"

export PYTHONPATH=.

python benchmarks/bm_ner.py --bm spacy_trf
