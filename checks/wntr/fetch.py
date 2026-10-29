#!/usr/bin/env python3
"""fetch.py MODE VERSION DIR - download WNTR from PyPI without running it.

MODE wheel: the wheel for this interpreter (cpXY) and this machine's manylinux
platform; MODE sdist: the source tarball. The file is chosen from PyPI's JSON
API, saved into DIR (which must be empty or absent: one download per
directory) and checked against the sha256 PyPI lists. Prints the saved path.
Exits 2 if PyPI has no such file (e.g. no wheel for aarch64 Linux). Fetching by
URL, not with `pip download`, because pip prepares an sdist's metadata by
running its setup.py. Python 3 standard library only.
"""
import hashlib
import json
import os
import platform
import sys
import urllib.request

sys.dont_write_bytecode = True


def main(a):
    if len(a) != 3 or a[0] not in ("wheel", "sdist"):
        print(__doc__)
        return 2
    mode, version, d = a
    with urllib.request.urlopen("https://pypi.org/pypi/wntr/%s/json" % version, timeout=60) as r:
        files = json.load(r)["urls"]
    if mode == "sdist":
        pick = [f for f in files if f["packagetype"] == "sdist"]
    else:
        cp = "-cp%d%d-" % sys.version_info[:2]
        m = platform.machine()
        pick = [f for f in files if f["packagetype"] == "bdist_wheel" and cp in f["filename"]
                and "linux" in f["filename"] and f["filename"].endswith("_%s.whl" % m)]
    if len(pick) != 1:
        print("no single %s of wntr %s for %s %s: %s" % (
            mode, version, platform.machine(), platform.python_version(),
            [f["filename"] for f in pick]), file=sys.stderr)
        return 2
    f = pick[0]
    os.makedirs(d, exist_ok=True)
    if os.listdir(d):
        print("%s is not empty" % d, file=sys.stderr)
        return 2
    path = os.path.join(d, f["filename"])
    with urllib.request.urlopen(f["url"], timeout=300) as r:
        data = r.read()
    got = hashlib.sha256(data).hexdigest()
    if got != f["digests"]["sha256"]:
        print("sha256 %s, PyPI lists %s" % (got, f["digests"]["sha256"]), file=sys.stderr)
        return 2
    with open(path, "wb") as out:
        out.write(data)
    print(path)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
