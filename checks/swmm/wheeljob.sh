#!/bin/sh
# wheeljob.sh WORK [VERSION]
#
# Runs the suite with the SWMM that pyswmm users actually get: swmm-toolkit's
# prebuilt wheel from PyPI, not a local build. Installs swmm-toolkit==VERSION
# (default 0.17.0) as a binary wheel into WORK/venv, records the wheel's file
# name and sha256, counts the FMA instructions in the libraries it ships, and
# runs every model in models.txt on one thread through the wheel's solver
# (swmmrun.py run, with a three-line runswmm stand-in). Writes
# WORK/runs/wheel-VERSION-PLATFORM/{digests.txt,wheel.txt}; compare those with
# swmmrun.py digcmp. WORK must hold src/suite/public (swmm-nrtestsuite).
# On Linux every run is pinned with taskset to SWMM_CPUS (default 0-3); on a
# shared host run it under nice -n 19. gate_control_2's .out is deleted after
# hashing. POSIX sh; needs python3 with venv and network access to PyPI.
set -eu
[ $# -ge 1 ] || { sed -n '2,16p' "$0"; exit 2; }
W=$(cd "$1" && pwd); V=${2:-0.17.0}
HERE=$(cd "$(dirname "$0")" && pwd)
sha256() { if command -v sha256sum >/dev/null 2>&1; then sha256sum "$1"; else shasum -a 256 "$1"; fi | cut -d' ' -f1; }

python3 -m venv "$W/venv"
"$W/venv/bin/pip" -q download --only-binary :all: --no-deps -d "$W/wheel" "swmm-toolkit==$V"
WHL=$(ls "$W/wheel"/swmm_toolkit-*.whl)
"$W/venv/bin/pip" -q install "$WHL"
PLAT=$(basename "$WHL" .whl | sed 's/.*-abi3-//; s/\..*//')
TAG=wheel-$V-$PLAT

cat > "$W/runswmm-wheel" <<EOF
#!/bin/sh
exec "$W/venv/bin/python" -I -c 'import sys
from swmm.toolkit import solver
solver.swmm_run(sys.argv[1], sys.argv[2], sys.argv[3])' "\$@"
EOF
chmod +x "$W/runswmm-wheel"

python3 -I "$HERE/swmmrun.py" run "$W/runswmm-wheel" "$W/src/suite/public" "$W/runs" "$TAG" 1 \
  --drop-out-over 100 $(grep -v '^#' "$HERE/models.txt")

INFO=$W/runs/$TAG/wheel.txt
{
  echo "wheel $(basename "$WHL") sha256 $(sha256 "$WHL")"
  echo "python $("$W/venv/bin/python" -c 'import platform; print(platform.python_version())')"
  echo "host $(uname -srm)"
  if command -v ldd >/dev/null 2>&1; then echo "libc $(ldd --version 2>&1 | head -1)"; fi
  if [ -r /proc/cpuinfo ]; then
    echo "cpu $(grep -m1 -E 'model name|^CPU part' /proc/cpuinfo | sed 's/.*: //')"
    echo "cpu has fma: $(grep -m1 -c -w -E 'fma|asimd' /proc/cpuinfo)"
  else
    echo "cpu $(sysctl -n machdep.cpu.brand_string 2>/dev/null)"
  fi
  for lib in $(find "$W/venv" -path '*swmm*' \( -name '*.so*' -o -name '*.dylib' -o -name '*.pyd' \) | sort); do
    n=n/a
    command -v objdump >/dev/null 2>&1 && n=$(objdump -d "$lib" 2>/dev/null | awk -F'\t' '{for (i = 2; i <= NF; i++) { split($i, w, " ");
          if (w[1] ~ /^(vfn?m(add|sub)[0-9a-z]*|fn?m(add|sub)|fml[as])$/) { n++; break } } } END { print n + 0 }')
    echo "lib ${lib#"$W"/venv/} sha256 $(sha256 "$lib" | cut -c1-16) fma $n"
  done
} > "$INFO"
cat "$INFO"
