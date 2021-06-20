#!/bin/bash

. "./env/bin/activate"

export PYTHONPATH=.

PROFILE_DIR='var/bm/profiles'

PROFILE_FILE="$PROFILE_DIR/tok-classla.pstat"

python benchmarks/bm_tok.py --bm classla --no-report --profile $PROFILE_FILE

echo "... cProfile statistics generated at: $PROFILE_FILE"

while [[ $# -ne 0 ]]
do
    arg="$1"
    case "$arg" in
        --interactive)
            snakeviz $PROFILE_FILE
            ;;
        *)
            ;;
    esac
    shift
done
