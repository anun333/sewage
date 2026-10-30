<!-- Draft, not posted. Checked 2026-10-30 against fau-evt/bsm2-python main at 73caa8b (unchanged since 2025-09-09) and IWA's Inf_rain_2006.txt and Inf_dry_2006.txt (sha256 c84a4e49... and 2a377665..., as in checks/bsm1/README.md). -->

**Title:** `data/raininfluent.csv` doesn't load: its flow column is written with thousands separators (`30.044.50` for 30044.5)

**Summary**

`src/bsm2_python/data/raininfluent.csv`, BSM1's rain-weather influent, can't be used as it is (checked at `main`, 73caa8b):

- **It doesn't load.** Rows 998, 1000 and 1001 hold the flows `30.044.50`, `27.446.67` and `26.880.33`. Passing the file as `data_in` to `BSM1OL`, or to any class that takes a file name, fails in `bsm_base.py`, which reads it with `np.array(list(csv.reader(f, delimiter=','))).astype(float)`:

  ```
  ValueError: could not convert string to float: '30.044.50'
  ```

- **The other flows would load 1000 times too small.** The flow column (Q, the 16th) is written with a dot as the thousands separator. IWA's `Inf_rain_2006.txt` has 21477 m³/d at t = 0, and this file has `21.477`; `dryinfluent.csv` has 21477. The three rows above are IWA's 30044.5, 27446.66667 and 26880.33333, written the same way with two decimals. All 1,344 flows follow this pattern.
- **Every value is rounded to 2 decimals, time included.** IWA's 15-minute samples (t = 0.010416667, 0.020833333, ...) become 0.01, 0.02, ..., so the intervals between rows vary from 0.01 to 0.03 d. With `timestep=None`, `bsm_base.py` takes its steps from these differences.
- **SI is right here, and worth keeping.** This file dilutes SI with the rain flow (30·Q_dry/Q_rain, to its 2 decimals), while IWA's hosted `Inf_rain_2006.txt` keeps SI at 30 g/m³. The BSM1 report's rain results need it diluted: its influent quality index is the same for dry and rain weather, as a pure dilution gives, and its effluent SI for rain is 22.8388, below 30.
- **Nothing in the package or its tests reads this file** (nor `dryinfluent.csv`), so the tests can't catch it. There's no storm-weather file.

`dryinfluent.csv`, for comparison, matches IWA's `Inf_dry_2006.txt` to 1e-8 in every column. Both files stop one row before IWA's last (t = 14).

**Expected behaviour:** `raininfluent.csv` loads, with Q in m³/d and the same precision as `dryinfluent.csv`.

**A possible fix:** rebuild `raininfluent.csv` from IWA's `Inf_rain_2006.txt` the way `dryinfluent.csv` was built, keeping SI diluted as this file does, and add a storm-weather file built the same way from `Inf_strm_2006.txt`. I'd be glad to open a PR with both files and the short script that builds them, if that's useful.

**Environment**
- bsm2-python `main` at 73caa8b
- IWA influent files from http://iwa-mia.org/wp-content/uploads/2019/04/ (`Inf_rain_2006.txt`, sha256 `c84a4e49d8c0f9bea27a427f528cd00344575c19900c8813eeffb66b0d1f5dd7`)

The comparison, with the numbers behind the SI point, is in https://github.com/anun333/sewage/tree/main/checks/bsm1.

Drafted with an AI assistant (Claude), which also ran the checks reported here; I read it before posting.
