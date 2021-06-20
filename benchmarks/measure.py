import logging
import os.path
import platform
import socket
from dataclasses import dataclass
from datetime import datetime
from functools import wraps
from pathlib import Path

import pandas as pd
import psutil
import time

LOG = logging.getLogger('measure')


@dataclass
class _Report:
    _dir = None
    _name = None
    _ctx = None
    _info = None
    _dfs = None # pending data-frames

    #

    @property
    def is_opened(self):
        return self._ctx is not None

    def open(self, dir_, prefix, info: dict):
        assert not self.is_opened

        self._dir = dir_
        self._name = prefix + self._now
        self._info = info
        self._dfs = None

        self._ctx = _Report._get_ctx()

        LOG.info("... opening report: {}".format(self._path))

    def close(self):
        assert self.is_opened

        if self._dfs:
            self._flush()
        self._ctx = None

    #

    def append(self, ts, func, execution_time, results):
        assert self.is_opened

        if self._dfs is None:
            self._dfs = []

        df = dict(self._ctx)

        if self._info:
            df.update(self._info)

        df['ts'] = ts
        df['func'] = func.__name__
        df['execution-time'] = execution_time

        if results:
            df.update(results)

        self._dfs.append(df)

    #

    @property
    def _path(self) -> str:
        return os.path.join(self._dir, "{}.csv".format(self._name))

    @property
    def _now(self) -> str:
        return "{:%Y%m%d_%H%M%S}".format(datetime.now())

    def _flush(self):
        assert self._dfs is not None

        df = pd.DataFrame()
        df = df.append(self._dfs, ignore_index=True, sort=False)

        p = self._path
        os.makedirs(Path(p).parent, exist_ok=True)

        LOG.info("... writing report: {}".format(p))
        df.to_csv(p)
        self._dfs = None

    @staticmethod
    def _get_ctx():
        try:
            return {'platform': platform.system(), 'platform-release': platform.release(),
                    # 'platform-version': platform.version(),
                    'architecture': platform.machine(),
                    'hostname': socket.gethostname(), 'processor': platform.processor(),
                    'ram-gb': str(round(psutil.virtual_memory().total / (1024.0 ** 3))),
                    'cpu-count': psutil.cpu_count()}
        except Exception as e:
            logging.exception(e)


_REPORT = _Report()


def open_report(dir_='var/bm/reports', prefix="report_", info=None):
    _REPORT.open(dir_, prefix, info)


def close_report():
    _REPORT.close()


#

def _report_entry(ts, func, duration, results):
    _REPORT.append(ts, func, duration, results)


#

def measure(func):
    @wraps(func)
    def _time_it(*args, **kwargs):
        start = time.perf_counter()
        LOG.info('func: {}'.format(func.__name__))

        ts = int(time.time())  # ts is part of report-entry as the func invocation timestamp

        results = {}
        try:
            results = func(*args, **kwargs)
        except BaseException as e:
            results = {'exception': e}
        finally:
            LOG.info('func: {}, results: {}'.format(func.__name__, results))
            duration = time.perf_counter() - start
            LOG.info('func: {}, execution-time: {:.3f} sec'.format(func.__name__, duration))
            if _REPORT.is_opened:
                _report_entry(ts, func, duration, results)
            return results

    return _time_it
