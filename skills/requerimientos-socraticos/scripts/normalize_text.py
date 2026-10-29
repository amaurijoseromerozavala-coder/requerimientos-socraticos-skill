#!/usr/bin/env python3
"""Create a new canonical UTF-8/LF file and report distinct raw/canonical hashes."""
import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path
from safe_io import canonical_lf, read_regular

def publish_new(destination, data):
    # Same-directory staging + atomic no-overwrite hard-link publication.
    # No destination exists until a full write and file fsync have succeeded.
    fd, temporary = tempfile.mkstemp(prefix='.normalize-', dir=destination.parent)
    try:
        offset = 0
        while offset < len(data):
            written = os.write(fd, data[offset:])
            if written <= 0:
                raise OSError('ZERO_LENGTH_WRITE')
            offset += written
        os.fchmod(fd, 0o600)
        os.fsync(fd)
        os.close(fd)
        fd = None
        os.link(temporary, destination, follow_symlinks=False)
    finally:
        if fd is not None:
            os.close(fd)
        os.unlink(temporary)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('source',type=Path);p.add_argument('destination',type=Path)
    args=p.parse_args()
    try:
        raw=read_regular(args.source.parent,args.source.name)
        normalized=canonical_lf(raw)
        # Exclusive creation never overwrites original receipts or existing data.
        publish_new(args.destination, normalized)
        print(json.dumps({'status':'NORMALIZED_COPY','raw_sha256':hashlib.sha256(raw).hexdigest(),'lf_sha256':hashlib.sha256(normalized).hexdigest(),'bytes':len(normalized),'existing_evidence_revalidated':False,'output_mode':'0600','access_contract':'OWNER_ONLY; external consumption requires an authorized transfer or explicit least-privilege access policy'}));return 0
    except (ValueError,OSError) as error:
        print(json.dumps({'status':'BLOCKED','error':str(error)}));return 1
if __name__=='__main__':raise SystemExit(main())
