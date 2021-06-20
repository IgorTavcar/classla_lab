import logging

import classla
import spacy
import torch
from thinc.backends import set_gpu_allocator
from thinc.util import require_gpu

import bm
import data
from measure import measure

LOG = logging.getLogger('bm_lem')


@measure
def bm_classla_lemmas_sl():
    return _classla(data.sl_size())


@measure
def bm_classla_identity_lemmas_sl():
    return _classla(data.sl_size(), identity=True)


@measure
def bm_classla_lemmas_500_sl():
    return _classla(500)


@measure
def bm_classla_identity_lemmas_500_sl():
    return _classla(500, identity=True)


@measure
def bm_spacy_lemmas_500_en():
    return _spacy(500)


@measure
def bm_spacy_lemmas_en():
    return _spacy(data.en_size())


@measure
def bm_spacy_lemmas_500_en_trf():
    return _spacy(500, model=bm.TRF_SPACY_MODEL)


@measure
def bm_spacy_lemmas_en_trf():
    return _spacy(data.en_size(), model=bm.TRF_SPACY_MODEL)


#

def _spacy(limit: int, model: str = bm.DEFAULT_SPACY_MODEL, cpu: bool = False):
    if cpu or not torch.cuda.is_available():
        spacy.require_cpu()
    else:
        set_gpu_allocator("pytorch")
        require_gpu(0)

    nlp = spacy.load(model, exclude=['ner'])
    n_sent = 0
    n_lem = 0
    count = 0
    for doc in nlp.pipe(data.en()):
        n_sent += sum(1 for _ in doc.sents)
        n_lem += sum(1 for token in doc if token.lemma_ != token.text.lower())
        count += 1
        if (count % (limit // 10)) == 0:
            LOG.info("... count: {} of {}".format(count, limit))
        if count >= limit:
            break
    return {'sentences': n_sent, 'lemmas': n_lem, 'count': count}


def _classla(limit: int, identity=False, cpu: bool = False):
    if identity:
        nlp = classla.Pipeline(processors='tokenize,lemma', dir=bm.CLASSLA_MODELS_DIR, lang='sl',
                               lemma_use_identity=True, use_gpu=not cpu)
    else:
        nlp = classla.Pipeline(processors='tokenize,pos,lemma', dir=bm.CLASSLA_MODELS_DIR, lang='sl', use_gpu=not cpu)

    n_sent = 0
    n_lem = 0
    count = 0
    for batch in data.sl():
        doc = nlp(batch)
        sentences = doc.sentences
        n_sent += len(sentences)
        n_lem += len(_lemmas(doc))
        count += 1
        if (count % (limit // 10)) == 0:
            LOG.info("... count: {} of {}".format(count, limit))
        if count >= limit:
            break
    return {'sentences': n_sent, 'lemmas': n_lem, 'count': count}


def _lemmas(doc) -> list:
    build = []
    for sentence in doc.sentences:
        for token in sentence.tokens:
            for word in token.words:
                dict = word.to_dict()
                if dict['text'].lower() != dict['lemma']:
                    build.append(word)
    return build


if __name__ == '__main__':
    benchmarks = {'classla': bm_classla_lemmas_sl,
                  'classla_quick': bm_classla_lemmas_500_sl,
                  'classla_idl': bm_classla_identity_lemmas_sl,
                  'classla_idl_quick': bm_classla_identity_lemmas_500_sl,
                  'spacy': bm_spacy_lemmas_en, 'spacy_quick': bm_spacy_lemmas_500_en,
                  'spacy_trf': bm_spacy_lemmas_en_trf, 'spacy_quick_trf': bm_spacy_lemmas_500_en_trf}
    bm.run("lem", benchmarks)
