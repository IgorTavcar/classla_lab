#!/bin/bash

. "./env/bin/activate"

export PYTHONPATH=.

python benchmarks/bm_pos.py --bm classla spacy_trf
python benchmarks/bm_ner.py --bm classla spacy_trf
python benchmarks/bm_lem.py --bm classla classla_idl spacy_trf