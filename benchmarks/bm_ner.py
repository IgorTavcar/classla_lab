import logging

import spacy
import torch
from thinc.backends import set_gpu_allocator
from thinc.util import require_gpu

import bm
import classla
import data
from measure import measure

LOG = logging.getLogger('bm_ner')


@measure
def bm_classla_ner_sl():
    return _classla(data.sl_size())


@measure
def bm_classla_ner_1000_sl():
    return _classla(1000)


@measure
def bm_spacy_ner_en():
    return _spacy(data.en_size())


@measure
def bm_spacy_ner_1000_en():
    return _spacy(1000)


@measure
def bm_spacy_ner_1000_en_trf():
    return _spacy(1000, model=bm.TRF_SPACY_MODEL)


@measure
def bm_spacy_ner_en_trf():
    return _spacy(data.en_size(), model=bm.TRF_SPACY_MODEL)


#

def _spacy(limit: int, model: str = bm.DEFAULT_SPACY_MODEL, cpu: bool = False):
    if cpu or not torch.cuda.is_available():
        spacy.require_cpu()
    else:
        set_gpu_allocator("pytorch")
        require_gpu(0)

    nlp = spacy.load(model, exclude=['lemmatizer'])
    n_sent = 0
    n_ne = 0
    count = 0
    for doc in nlp.pipe(data.en()):
        n_sent += sum(1 for _ in doc.sents)
        n_ne += sum(1 for _ in doc.ents)
        count += 1
        if (count % (limit // 10)) == 0:
            LOG.info("... count: {} of {}".format(count, limit))
        if count >= limit:
            break
    return {'sentences': n_sent, 'ne': n_ne, 'count': count}


def _classla(limit: int, cpu: bool = False):
    nlp = classla.Pipeline(processors='tokenize,ner', dir=bm.CLASSLA_MODELS_DIR, lang='sl', use_gpu=not cpu)
    n_sent = 0
    n_ne = 0
    count = 0
    for line in data.sl():
        doc = nlp(line)
        sentences = doc.sentences
        n_sent += len(sentences)
        n_ne += len(_ne(doc))
        count += 1
        if (count % (limit // 10)) == 0:
            LOG.info("... count: {} of {}".format(count, limit))
        if count >= limit:
            break
    return {'sentences': n_sent, 'ne': n_ne, 'count': count}


def _ne(doc) -> list:
    build = []
    for sentence in doc.sentences:
        for token in sentence.tokens:
            if token.ner != 'O':
                build.append(token)
    return build


if __name__ == '__main__':
    benchmarks = {'classla': bm_classla_ner_sl, 'classla_quick': bm_classla_ner_1000_sl,
                  'spacy': bm_spacy_ner_en, 'spacy_quick': bm_spacy_ner_1000_en,
                  'spacy_trf': bm_spacy_ner_en_trf, 'spacy_quick_trf': bm_spacy_ner_1000_en_trf}
    bm.run("ner", benchmarks)
