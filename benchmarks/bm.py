import argparse
import cProfile
import logging
import os
from importlib.metadata import version
from pathlib import Path

import time
import torch

from measure import close_report
from measure import open_report

__VERSION__ = "1.0.2"

LOG = logging.getLogger('bm')

CLASSLA_MODELS_DIR = 'var/bm/models'
DEFAULT_SPACY_MODEL = 'en_core_web_md'
TRF_SPACY_MODEL = 'en_core_web_trf'


def run(name: str, benchmarks: dict):
    all_ = sorted(benchmarks.keys())

    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(name)s -   %(message)s",
        datefmt="%m/%d/%Y %H:%M:%S",
        level=logging.INFO,
    )

    LOG.info("running benchmarks: {} - {}".format(name, all_))

    if torch.cuda.is_available():
        LOG.info("... CUDA devices: {}".format(torch.cuda.device_count()))
        LOG.info("... ... current: {}".format(torch.cuda.current_device()))
        LOG.info("... ... name: {}".format(torch.cuda.get_device_name(torch.cuda.current_device())))
    else:
        LOG.info("... CUDA not available")

    parser = argparse.ArgumentParser()
    parser.add_argument('--bm',
                        nargs='+',
                        help="benchmark: all or {} | default=all".format(all_),
                        default='all')
    parser.add_argument('--no-report', action='store_true', help='Don\'t generate report at var/bm/reports.')
    parser.add_argument('--profile', default=None, help='Path where collected cProfile stats are generated'
                                                        ' | default=None')
    parser.add_argument('--cpu', action='store_true', help='Disable CUDA.')
    parser.set_defaults(no_report=False)
    parser.set_defaults(cpu=False)
    args = parser.parse_args()

    LOG.info("... args: {}".format(args))

    if args.cpu:
        accelerator = "cpu[preferred]"
    elif not torch.cuda.is_available():
        accelerator = "cpu[no-cuda-available]"
    else:
        accelerator = "cuda[{}]".format(torch.cuda.get_device_name(torch.cuda.current_device()))

    LOG.info("... engaged accelerator: {}".format(accelerator))
    LOG.info("... classla version: {}".format(version('classla')))
    LOG.info("... obeliks version: {}".format(version('obeliks')))
    LOG.info("... torch version: {}".format(version('torch')))

    if not args.no_report:
        tag = "{}-{}".format(name, _format_bm(args.bm))
        open_report(prefix=tag + "-", info={'tag': tag,
                                            'bm-version': __VERSION__,
                                            'classla-v': version('classla'),
                                            'obeliks-v': version('obeliks'),
                                            'torch-v': version('torch'),
                                            'accelerator': accelerator})

    profile_file = args.profile

    pr = None
    if profile_file is not None:
        LOG.info("... running cProfile profiler!")
        os.makedirs(Path(profile_file).parent, exist_ok=True)
        pr = cProfile.Profile()

    if isinstance(args.bm, list):
        bms = args.bm
    elif args.bm == 'all':
        bms = all_
    elif args.bm in benchmarks:
        bms = [args.bm]
    else:
        raise Exception("unknown benchmark: {}".format(args.bm))

    for bm in bms:
        if pr is not None:
            pr.enable()
        benchmarks[bm]()
        if pr is not None:
            pr.disable()
        time.sleep(1)

    if pr is not None:
        LOG.info("see cProfile stats: {}".format(profile_file))
        pr.dump_stats(profile_file)

    if not args.no_report:
        close_report()

    LOG.info("completed, bye bye!")


def _format_bm(bm):
    if isinstance(bm, list):
        return '-'.join(bm)
    return bm
