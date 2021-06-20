import logging

import spacy
import torch
from thinc.api import set_gpu_allocator, require_gpu

import bm
import classla
import data
from measure import measure

LOG = logging.getLogger('bm_pos')


@measure
def bm_classla_pos_sl():
    return _classla(data.sl_size())


@measure
def bm_classla_pos_100_sl():
    return _classla(100)


@measure
def bm_spacy_pos_en():
    return _spacy(data.en_size())


@measure
def bm_spacy_pos_100_en():
    return _spacy(100)


@measure
def bm_spacy_pos_100_en_trf():
    return _spacy(100, model=bm.TRF_SPACY_MODEL)


@measure
def bm_spacy_pos_en_trf():
    return _spacy(data.en_size(), model=bm.TRF_SPACY_MODEL)


#

def _spacy(limit: int, model: str = bm.DEFAULT_SPACY_MODEL, cpu: bool = False):
    if cpu or not torch.cuda.is_available():
        spacy.require_cpu()
    else:
        set_gpu_allocator("pytorch")
        require_gpu(0)

    nlp = spacy.load(model, exclude=['ner', 'lemmatizer'])
    n_sent = 0
    n_nouns = 0
    count = 0
    for doc in nlp.pipe(data.en()):
        n_sent += sum(1 for _ in doc.sents)
        n_nouns += sum(1 for _ in doc.noun_chunks)
        count += 1
        if (count % (limit // 10)) == 0:
            LOG.info("... count: {} of {}".format(count, limit))
        if count >= limit:
            break
    return {'sentences': n_sent, 'nouns': n_nouns, 'count': count}


def _classla(limit: int, cpu: bool = False):
    nlp = classla.Pipeline(processors='tokenize,pos', dir=bm.CLASSLA_MODELS_DIR, lang='sl', use_gpu=not cpu)
    n_sent = 0
    n_nouns = 0
    count = 0
    for line in data.sl():
        doc = nlp(line)
        sentences = doc.sentences
        n_sent += len(sentences)
        for sent in sentences:
            n_nouns += sum(1 for token in sent.tokens if token.to_dict(['upos'])[0]['upos'] == 'NOUN')
        count += 1
        if (count % (limit // 10)) == 0:
            LOG.info("... count: {} of {}".format(count, limit))
        if count >= limit:
            break
    return {'sentences': n_sent, 'nouns': n_nouns, 'count': count}


if __name__ == '__main__':
    benchmarks = {'classla': bm_classla_pos_sl, 'classla_quick': bm_classla_pos_100_sl,
                  'spacy': bm_spacy_pos_en, 'spacy_quick': bm_spacy_pos_100_en,
                  'spacy_trf': bm_spacy_pos_en_trf, 'spacy_quick_trf': bm_spacy_pos_100_en_trf}
    bm.run("pos", benchmarks)
