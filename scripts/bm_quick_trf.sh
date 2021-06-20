#!/bin/bash

. "./env/bin/activate"

export PYTHONPATH=.

python benchmarks/bm_pos.py --bm classla_quick spacy_quick_trf
python benchmarks/bm_ner.py --bm classla_quick spacy_quick_trf
python benchmarks/bm_lem.py --bm classla_quick classla_idl_quick spacy_quick_trf