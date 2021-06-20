import logging

import classla
import spacy

import bm
import data
from measure import measure

LOG = logging.getLogger('bm_tok')


@measure
def bm_sentences_classla_obeliks_sl():
    nlp = classla.Pipeline(processors='tokenize', dir=bm.CLASSLA_MODELS_DIR, lang='sl')
    n = 0
    for line in data.sl():
        doc = nlp(line)
        n += len(doc.sentences)
    return {'sentences': n}


@measure
def bm_sentences_classla_obeliks_joined_sl():
    # This benchmark shows the speed of the obeliks tokenizer that would be (approximately) achieved
    # ... if the hotspot problem was fixed.
    nlp = classla.Pipeline(processors='tokenize', dir=bm.CLASSLA_MODELS_DIR, lang='sl')
    str = " ".join(data.sl())
    doc = nlp(str)
    return {'sentences': len(doc.sentences)}


@measure
def bm_sentences_classla_obeliks_batched_sl():
    # This benchmark is based on naive assumption that batching of input samples is supported.
    # Splitting the samples in lines does not improve the performance of the pipeline.
    nlp = classla.Pipeline(processors='tokenize', dir=bm.CLASSLA_MODELS_DIR, lang='sl')
    n = 0
    for batch in data.sl(50):
        doc = nlp('\n'.join(batch))  # lists are not supported
        n += len(doc.sentences)
    return {'sentences': n}


@measure
def bm_sentences_classla_reldi_sl():
    nlp = classla.Pipeline(processors='tokenize', dir=bm.CLASSLA_MODELS_DIR, tokenize_library='reldi', lang='sl')
    n = 0
    for line in data.sl():
        doc = nlp(line)
        n += len(doc.sentences)
    return {'sentences': n}


@measure
def bm_sentences_classla_multi_docs_sl():
    # This invocation will raise for classla versions <= 1.0.1.
    # ... Multi-docs is a feature of stanza v1.2., but is not implemented in classla~=1.0.1.
    nlp = classla.Pipeline(processors='tokenize', dir=bm.CLASSLA_MODELS_DIR, lang='sl')
    n = 0
    for docs in data.sl_docs(64):
        result = nlp(docs)
        n += sum(len(doc.sentences) for doc in result)
    return {'sentences': n}


@measure
def bm_sentences_spacy_3cpu_en():
    nlp = spacy.load(bm.DEFAULT_SPACY_MODEL, exclude=['ner', 'attribute_ruler', 'lemmatizer'])
    n = 0
    for doc in nlp.pipe(data.en(), n_process=3):
        n += sum(1 for _ in doc.sents)
    return {'sentences': n}


@measure
def bm_sentences_spacy_en():
    nlp = spacy.load(bm.DEFAULT_SPACY_MODEL, exclude=['ner', 'attribute_ruler', 'lemmatizer'])
    n = 0
    for doc in nlp.pipe(data.en()):
        n += sum(1 for _ in doc.sents)
    return {'sentences': n}


@measure
def bm_sentences_spacy_fast_en():
    nlp = spacy.load(bm.DEFAULT_SPACY_MODEL,
                     exclude=["tok2vec", "tagger", "parser", "attribute_ruler", "lemmatizer", "ner"])
    nlp.add_pipe('sentencizer')
    n = 0
    for doc in nlp.pipe(data.en()):
        n += sum(1 for _ in doc.sents)
    return {'sentences': n}


if __name__ == '__main__':
    benchmarks = {'classla': bm_sentences_classla_obeliks_sl,
                  'classla_reldi': bm_sentences_classla_reldi_sl,
                  'classla_joined': bm_sentences_classla_obeliks_joined_sl,
                  'classla_batched': bm_sentences_classla_obeliks_batched_sl,
                  'classla_multi_docs': bm_sentences_classla_multi_docs_sl,
                  'spacy': bm_sentences_spacy_en,
                  'spacy_parallel': bm_sentences_spacy_3cpu_en,
                  'spacy_fast': bm_sentences_spacy_fast_en}
    bm.run("tok", benchmarks)
