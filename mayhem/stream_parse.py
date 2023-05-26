#! /usr/bin/env python3
import atheris
import sys
import fuzz_helpers
import io
from contextlib import contextmanager


with atheris.instrument_imports():
    from streaming_form_data import StreamingFormDataParser, ParseFailedException
    from streaming_form_data.targets import ValueTarget
ctr = 0

def TestOneInput(data):
    global ctr
    ctr += 1
    fdp = fuzz_helpers.EnhancedFuzzedDataProvider(data)
    try:
        parser = StreamingFormDataParser(fuzz_helpers.build_fuzz_dict(fdp, [str,str]))
        parser.register(fdp.ConsumeRandomString(), ValueTarget())
        parser.data_received(fdp.ConsumeRemainingBytes())
    except (ParseFailedException, ValueError):
        return -1
def main():
    atheris.Setup(sys.argv, TestOneInput)
    atheris.Fuzz()


if __name__ == "__main__":
    main()
