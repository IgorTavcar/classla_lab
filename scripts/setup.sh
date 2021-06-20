#!/bin/bash

. "./env/bin/activate"

export PYTHONPATH=.

VAR_DIR=./var/bm
mkdir -p $VAR_DIR

MODELS_DIR=$VAR_DIR/models
mkdir -p $MODELS_DIR

python -m pip install -U pip setuptools wheel
python -m pip install -U spacy[transformers,cuda112]

python -m spacy download en_core_web_md
python -m spacy download en_core_web_trf

python -c "import classla; classla.download(lang='sl', dir='${MODELS_DIR}', logging_level='info')" || echo "failed to download slo model"
