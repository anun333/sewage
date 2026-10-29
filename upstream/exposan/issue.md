<!-- DRAFT for QSD-Group/EXPOsan (bugs--errors--warnings template). Not posted; reviewed before posting. -->

**Title:** bsm1: steady state differs from the BSM1 reference by up to 0.7%, because of the exact stoichiometric constants and alkalinity weights; with BSM1's rounded constants it matches to 1e-8

**Describe the problem**

I compared `exposan.bsm1` (open loop) with the BSM1 report (Alex et al. 2008, LTH-IEA-7229, Tables 6-8 and Appendix 4) and with two other implementations. One is bsm2-python, whose converged BSM1 matches the BSM group's Simulink to 1e-8; the other is WaterTAP. Steady state means 1000 days at constant influent, BDF at rtol = atol = 1e-8, from the module's default initial state.

- **As shipped**, 86 of 108 values in Tables 6-8 match to the printed digits, and the largest difference from bsm2-python is 0.7% (reactor 2 S_NO: 3.6362 against 3.6620). Effluent S_NO is −0.27%, S_O −0.15% and S_NH +0.16%.
- **Cause 1: the stoichiometric constants.** `exposan/bsm1/data/_asm1.tsv` uses the exact values, 20/7 (2.857) in anoxic growth (line 3, `7/20*(Y_H-1)/Y_H`) and 32/7 (4.571) in autotrophic growth (line 4, `(Y_A-32/7)/Y_A`). `qsdsan/data/process_data/_asm1.tsv` does the same. BSM1 specifies the rounded 2.86 and 4.57. With those two constants swapped in:
  - 104 of 108 values in Tables 6-8 match;
  - every state matches bsm2-python to 1.1e-8, except alkalinity.
- **Cause 2: alkalinity.** QSDsan derives the S_ALK coefficients from a charge balance with exact atomic weights: S_ALK as HCO3⁻ at 1/12.0107 charge per g C, and nitrate and ammonium at 1/14.0067 per g N. BSM1's equations divide by 14, and its 7 mol/m³ input is written as 7 × 12 = 84 g C/m³. So each alkalinity change is f = 14/14.0067 × 12.0107/12 = 1.000413 times BSM1's. That predicts effluent S_ALK lower by (7 − 4.12558) × (f − 1) = 0.0011868, and the run gives exactly that: 4.12439 against bsm2-python's 4.12558.

The exact constants close the COD and nitrogen balances, and BSM1's rounded ones don't, so this is a trade-off rather than a bug. But a module named `bsm1` is the one people will use to check a controller against the published benchmark, and today it can't reproduce it beyond about 3e-3. Two options:
- a `bsm1` stoichiometry option, with 2.86/4.57 and the 12/14 alkalinity convention;
- or a note in the module's docs saying how far it stands from the reference, and why.

Two smaller things only change dynamic runs. I haven't isolated their effects:
- **The internal recycle follows the influent.** `CSTR.split` is normalised to fractions (`qsdsan/unit_operations/dynamic/_bioreactor.py:267`), so `split=[Q_intr, Q+Q_ras]` (`exposan/bsm1/system.py:274`) becomes a fixed 0.6 of O3's outflow. Under the dry-weather file that gives Qa = 1.5 × (Q0 + Qr), where BSM1's open loop holds Qa at 55338 m³/d. At constant influent the two agree, so the steady state above isn't affected.
- **The clarifier keeps the solubles in one mixed volume** (`_clarifier.py:553`), where BSM1 layers them in ten. In one dry-weather run with the recycle held at 55338 (days 7-14):
  - EQ is +0.73% and effluent TSS within 4e-6 of the report;
  - but the 95th percentile of effluent ammonia is 7.81 against 8.88, and the time over the total-N limit 0.06 against 0.57 days.
  
  The solids track bsm2-python to about 0.1%. The damping of the soluble peaks fits a single mixed volume, but that is inferred from the series, not shown by a run.

**To Reproduce**

The scripts and results are at https://github.com/anun333/sewage/tree/main/checks/bsm1. `run_qsdsan.py` runs `exposan.bsm1` as shipped and, with `bsm1`, with the two constants replaced in a copy of `_asm1.tsv`:

```sh
python run_qsdsan.py ss results/ss_qsdsan.csv 1000 1e-8              # as shipped
python run_qsdsan.py ss results/ss_qsdsan_bsm1coef.csv 1000 1e-8 bsm1  # 2.86 and 4.57
python bsm1cmp.py ref reference.csv results/ss_qsdsan.csv --source t   # 86 of 108 agree
python bsm1cmp.py pair results/ss_bsm2python.csv results/ss_qsdsan_bsm1coef.csv --rtol 1e-7
                                                                        # only the 8 S_ALK rows differ
```

The replacement:

```python
txt.replace('7/20*(Y_H-1)/Y_H', '(Y_H-1)/(2.86*Y_H)') \
   .replace('7/20*(1-Y_H)/Y_H', '(1-Y_H)/(2.86*Y_H)') \
   .replace('(Y_A-32/7)/Y_A', '(Y_A-4.57)/Y_A')
```

`reference.csv` holds the report's numbers with their pages. `bsm1cmp.py` compares to the printed digits.

**Screenshots**

NA

**Environment**

1. Versions:
   - EXPOsan 1.6.0 (`main` at 84d5034), installed with `--no-deps`, since its `pyproject.toml` pins `qsdsan==1.5.3`;
   - QSDsan 1.6.0 (`main` at bac88d8);
   - BioSTEAM 2.54.0, Thermosteam 0.54.2, SciPy 1.18.1, NumPy 2.5.4.
2. Debian 13 x86-64, Python 3.13.5.

The relevant files haven't changed on `main` since.

**Additional context**

- The BSM1 reference itself has two problems, documented in the README linked above:
  - the IWA-hosted rain and storm files keep S_I at 30 where the published results need it diluted;
  - Appendix 4's steady state misses the X_I balance by 6e-6.
  
  Neither affects the comparison above.
- I'm happy to open a PR for whichever option you prefer.

Drafted with an AI assistant (Claude), which also ran the builds and checks reported here; I read it before posting.
