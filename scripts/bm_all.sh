#!/bin/bash

. "./env/bin/activate"

export PYTHONPATH=.

python benchmarks/bm_tok.py

python benchmarks/bm_pos.py --bm classla_quick spacy_quick
python benchmarks/bm_ner.py --bm classla_quick spacy_quick
python benchmarks/bm_lem.py --bm classla_quick classla_idl_quick spacy_quick

python benchmarks/bm_pos.py
python benchmarks/bm_ner.py
python benchmarks/bm_lem.py

python benchmarks/bm_pos.py --bm classla spacy_trf
python benchmarks/bm_ner.py --bm classla spacy_trf
python benchmarks/bm_lem.py --bm classla classla_idl spacy_trf