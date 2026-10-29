<!-- DRAFT for USEPA/WNTR (bug-report template). Not posted; reviewed before posting. -->

**Title:** WNTRSimulator results change from run to run: the evaluator orders variables and constraints by memory address

**Summary**

Running the same network twice with `WNTRSimulator`, on the same machine and installation, gives different results. Usually they differ in the last digits. On networks with controls they can differ by metres of pressure and by pump status.

**The cause** (all at the 1.5.0 tag):
- `wntr/sim/aml/evaluator.hpp:161-165` keeps the model in `std::set<Var*>`, `std::set<Param*>`, `std::set<Float*>`, `std::set<Constraint*>` and `std::set<IfElseConstraint*>`. These are ordered by pointer value.
- `Evaluator::set_structure()` (`evaluator.cpp`, from line 412) numbers variables and constraints by iterating those sets, so the Jacobian's rows and columns come out in heap-address order.
- Within a constraint, the derivative terms are in `std::map<Var*, ...>` (`evaluator.hpp:95`, `116`, `120`), also ordered by pointer.
- That order reaches `spsolve(J, r, permc_spec="COLAMD")` (`solvers.py:178`). There it changes the column ordering and so the rounding of each Newton step.

Heap addresses change with ASLR, `PYTHONHASHSEED` and whatever Python allocated earlier, so each run can number the equations differently.

**What it does to results.** I ran five runs of the x86-64 manylinux wheel on one machine, with the same script and no other changes:
- **Small networks** differ in the last digits: Net1 by up to 9.2e-13 relative and Net3 by 7.7e-10, the largest in flows near zero. All pass an `allclose` at rtol 0.01 and atol 1e-6.
- **Net6** (96 h, pumps and valves under controls) fails that `allclose` in every pair of runs. A rounding difference moves a tank level or pressure across a control threshold at a different step, and the run then follows a different path:

| run (same machine, same wheel) | JUNCTION-1100 pressure, 24 h (m) | PUMP-3863, 24 h | JUNCTION-3322 pressure, 82 h (m) |
| --- | ---: | --- | ---: |
| 1 | 8.655 | closed | 209.29 |
| 2 | 1.019 | open | 209.28 |
| 3 | 8.655 | closed | 229.79 |
| 4 | 1.019 | open | 209.28 |
| 5 | 1.019 | open | 209.29 |

A separate check, with three runs side by side under different `PYTHONHASHSEED` values, gave one run 0.84 m of pressure away from the other two (40.60 against 39.76 m at hour 96).

**Expected behaviour:** the same model and inputs give the same results on the same machine. A possible fix is to order by something stable instead of by address:
- for example, a serial number given to each `Var`, `Param`, `Float` and `Constraint` when it is created, with the sets and the `jac_rpn` maps ordered by it;
- or vectors kept in insertion order next to the sets.

Python builds the model in the same order every time, so the equation order would then repeat. Net6 would still be sensitive to rounding across compilers and CPUs because of its control thresholds, but a run would be repeatable, and differences between builds could be told apart from run-to-run noise.

**Example**

```python
import hashlib, sys, numpy as np, wntr
wn = wntr.network.WaterNetworkModel("examples/networks/Net3.inp")
r = wntr.sim.WNTRSimulator(wn).run_sim()
p = r.node["pressure"]; p = p[sorted(p.columns)]
print(hashlib.sha256(np.ascontiguousarray(p.values).tobytes()).hexdigest()[:16])
```

Run it three times, for example with `PYTHONHASHSEED=1`, `2` and `3`. The three hashes differ. Use Net6 instead of Net3 to see differences beyond `allclose`; each run takes about two minutes.

**Environment**
 - Operating system: Ubuntu 24.04, x86-64 (AMD Ryzen 5 PRO 5650U); also Debian 13 aarch64 with the sdist build, where the same happens
 - Python version: 3.12.3 (x86-64), 3.13.5 (aarch64)
 - WNTR version: 1.5.0 (manylinux x86_64 wheel; sdist build on aarch64)

**Additional context**

- Building the extensions with `-ffp-contract=off` changes no machine code in them, so this is not a fused-multiply-add effect.
- The full record, with all runs, the Net6 values at more points, and the scripts, is at https://github.com/anun333/sewage/tree/main/checks/wntr.

Drafted with an AI assistant (Claude), which also ran the builds and checks reported here; I read it before posting.
