# Third-party material

Everything in this repository is MIT licensed ([LICENSE](LICENSE)) except as listed
here. Checked 2026-10-29.

## Copied into this repository

### checks/bsm1/simulink200.csv

Its 24 values are copied from bsm2-python, `tests/bsm1_ol_test.py` lines 62-114 at
commit 73caa8bde193c0dd8a8803dfcd67b546501c950e
(https://github.com/fau-evt/bsm2-python): the BSM2 group's Simulink results for BSM1
open loop after 200 days. bsm2-python is distributed under this licence:

    BSD 3-Clause License

    Copyright (c) 2025, FAU-EVT

    Redistribution and use in source and binary forms, with or without
    modification, are permitted provided that the following conditions are met:

    1. Redistributions of source code must retain the above copyright notice, this
       list of conditions and the following disclaimer.

    2. Redistributions in binary form must reproduce the above copyright notice,
       this list of conditions and the following disclaimer in the documentation
       and/or other materials provided with the distribution.

    3. Neither the name of the copyright holder nor the names of its
       contributors may be used to endorse or promote products derived from
       this software without specific prior written permission.

    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
    AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
    IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
    DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
    FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
    DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
    SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
    CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
    OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
    OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

### checks/bsm1/reference.csv

Numbers from IWA Task Group on Benchmarking of Control Strategies for WWTPs,
*Benchmark Simulation Model no. 1 (BSM1)*, Lund University, 2008,
LUTEDX/(TEIE-7229), each with its page. The report states no licence and is not
included here; only the printed numbers are copied, not its text, tables or figures.

## Derived from, not included

- **swmm-nrtestsuite v3.3.0** (https://github.com/pyswmm/swmm-nrtestsuite, CC BY 4.0,
  copyright its contributors, with US government material in the public domain):
  `checks/swmm/digests/` holds SHA-256 digests of SWMM outputs computed from its
  models, and `checks/swmm/models.txt` lists their names. The models are not included.
- **HSL.** The WaterTAP results in `checks/bsm1/` were computed with IPOPT 3.13.2 from
  idaes-ext 3.4.2, using the HSL linear solver MA27. HSL, a collection of Fortran codes
  for large-scale scientific computation. See http://www.hsl.rl.ac.uk.
- **CORE-MATH** (https://core-math.gitlabpages.inria.fr/, MIT). `checks/swmm/crshim.sh`
  compiles CORE-MATH sources from a checkout given on its command line;
  `checks/swmm/crlibm_shim*.c` only call CORE-MATH's `cr_*` functions. No CORE-MATH
  file is in this repository. Anyone who distributes a built shim must include
  CORE-MATH's copyright notices and licence.
- **BSM1 inputs.** IWA's influent and sensor-noise files (http://iwa-mia.org/benchmarking/,
  no terms stated) are downloaded by the commands in `checks/bsm1/README.md` and are
  not included; their SHA-256 values are recorded there.

## upstream/swmm/

The patches change SWMM: public domain (US EPA), with MIT-licensed additions by the
pyswmm fork's contributors. The unchanged context lines remain under SWMM's terms. Our
changes in them are MIT licensed and also dedicated to the public domain under CC0 1.0
(https://creativecommons.org/publicdomain/zero/1.0/), so the pyswmm fork and US EPA can
each take them on their own terms.

## AI assistance

Much of the text, code and analysis here was produced with an AI assistant (Claude, by
Anthropic), which also ran the builds and checks. The maintainer reads and approves what
is published here and upstream. `thread/2026-10-27-initial.md` is an AI assistant's
answer, kept verbatim and unchecked.
