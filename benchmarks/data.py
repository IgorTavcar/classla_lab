__EN_TEXT_FILE__ = 'data/text/raw-en.txt'
__SL_TEXT_FILE__ = 'data/text/raw-slo.txt'

from classla import Document


def sl_docs(batch_size=1):
    if batch_size == 1:
        yield [Document([], text=next(sl(batch_size)))]
    else:
        yield [Document([], text=d) for d in sl(batch_size)]


def sl(batch_size=1):
    yield from _generator(__SL_TEXT_FILE__, batch_size)


def en(batch_size=1):
    yield from _generator(__EN_TEXT_FILE__, batch_size)


def en_size() -> int:
    return sum(1 for _ in open(__EN_TEXT_FILE__, 'rb'))


def sl_size() -> int:
    return sum(1 for _ in open(__SL_TEXT_FILE__, 'rb'))


def _generator(file, batch_size):
    assert batch_size > 0

    # note: yields str (if batch_size is 1) or list[str] if batch_size gt 1
    with open(file, encoding='utf-8') as reader:
        assert batch_size >= 1

        if batch_size > 1:
            batch = []
        for line in reader:
            if batch_size == 1:
                yield line.rstrip()
            else:
                batch.append(line.rstrip())
                if len(batch) == batch_size:
                    yield batch
                    batch.clear()
        if batch_size > 1 and len(batch) > 0:
            yield batch
