#!/bin/bash

. "./env/bin/activate"

export PYTHONPATH=.

PROFILE_DIR='var/bm/profiles'

NOW=$(date +"%Y%m%d_%H%M%S")

PROFILE_FILE="${PROFILE_DIR}/${NOW}_lem-classla-q.pstat"
PROFILE_FILE_2="${PROFILE_DIR}/${NOW}_lem-classla_idl-q.pstat"

python benchmarks/bm_lem.py --bm classla_quick --no-report --profile "$PROFILE_FILE"
python benchmarks/bm_lem.py --bm classla_idl_quick --no-report --profile "$PROFILE_FILE_2"

echo "... cProfile statistics generated at: $PROFILE_FILE"
echo "... cProfile statistics generated at: $PROFILE_FILE_2"

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

