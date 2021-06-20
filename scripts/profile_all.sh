#!/bin/bash

. "./env/bin/activate"

export PYTHONPATH=.

PROFILE_DIR='var/bm/profiles'

NOW=$(date +"%Y%m%d_%H%M%S")

PROFILE_FILE_TOK="${PROFILE_DIR}/${NOW}_tok-classla.pstat"

PROFILE_FILE_POS_Q="${PROFILE_DIR}/${NOW}_pos-classla-q.pstat"
PROFILE_FILE_NER_Q="${PROFILE_DIR}/${NOW}_ner-classla-q.pstat"
PROFILE_FILE_LEM_Q="${PROFILE_DIR}/${NOW}_lem-classla-q.pstat"
PROFILE_FILE_LEM_IDL_Q="${PROFILE_DIR}/${NOW}_lem-classla_idl-q.pstat"

PROFILE_FILE_POS="${PROFILE_DIR}/${NOW}_pos-classla.pstat"
PROFILE_FILE_NER="${PROFILE_DIR}/${NOW}_ner-classla.pstat"
PROFILE_FILE_LEM="${PROFILE_DIR}/${NOW}_lem-classla.pstat"
PROFILE_FILE_LEM_IDL="${PROFILE_DIR}/${NOW}_lem-classla_idl.pstat"

python benchmarks/bm_tok.py --bm classla --no-report --profile "$PROFILE_FILE_TOK"

python benchmarks/bm_pos.py --bm classla_quick --no-report --profile "$PROFILE_FILE_POS_Q"
python benchmarks/bm_ner.py --bm classla_quick --no-report --profile "$PROFILE_FILE_NER_Q"
python benchmarks/bm_lem.py --bm classla_quick --no-report --profile "$PROFILE_FILE_LEM_Q"
python benchmarks/bm_lem.py --bm classla_idl_quick --no-report --profile "$PROFILE_FILE_LEM_IDL_Q"

python benchmarks/bm_pos.py --bm classla --no-report --profile "$PROFILE_FILE_POS"
python benchmarks/bm_ner.py --bm classla --no-report --profile "$PROFILE_FILE_NER"
python benchmarks/bm_lem.py --bm classla --no-report --profile "$PROFILE_FILE_LEM"
python benchmarks/bm_lem.py --bm classla_idl --no-report --profile "$PROFILE_FILE_LEM_IDL"

echo "... cProfile statistics generated at: $PROFILE_FILE_TOK"

echo "... cProfile statistics generated at: $PROFILE_FILE_POS_Q"
echo "... cProfile statistics generated at: $PROFILE_FILE_NER_Q"
echo "... cProfile statistics generated at: $PROFILE_FILE_LEM_Q"
echo "... cProfile statistics generated at: $PROFILE_FILE_LEM_IDL_Q"

echo "... cProfile statistics generated at: $PROFILE_FILE_POS"
echo "... cProfile statistics generated at: $PROFILE_FILE_NER"
echo "... cProfile statistics generated at: $PROFILE_FILE_LEM"
echo "... cProfile statistics generated at: $PROFILE_FILE_LEM_IDL"
