#!/usr/bin/env python3
"""Internal supervised consumer of bounded Git documentation bytes on stdin."""
import os
import sys

MEMORY_FAILURE = b'{"status":"INVALID","error":"MEMORY_BUDGET_EXCEEDED"}\n'


def main():
    try:
        import json
        from pathlib import Path, PurePosixPath
        from document_source import MemorySource
        from git_bundle import read_bundle
        from memory_budget import observe_process_memory
        from validate_prd import validate_prd
        prd, files, oids = read_bundle(sys.stdin.buffer)
        source = MemorySource(files, oids)
        result = validate_prd(Path(prd), source=source.scope(str(PurePosixPath(prd).parent)))
        print(json.dumps({'document_validation': result, 'consumed_files': source.consumed_files,
                          'memory_observation': observe_process_memory()}, ensure_ascii=True))
        return 0
    except MemoryError:
        os.write(1, MEMORY_FAILURE)
        return 1
    except (OSError, ValueError, KeyError, RecursionError) as error:
        import json
        print(json.dumps({'status': 'INVALID', 'error': str(error)}, ensure_ascii=True))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
