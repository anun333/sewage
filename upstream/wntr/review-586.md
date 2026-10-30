<!-- Draft, not posted. A review comment on USEPA/WNTR#586 (monocongo, opened 2026-10-30, "fix: order AML evaluator variables and constraints by creation serial"), which implements the design proposed in #585. Our own branch (pr-585.md) is the same design and is not to be opened. Evidence: upstream/wntr/fixcheck.sh, perfcheck.sh, swigcheck.sh runs on cfarm421 and cfarm424, 2026-10-30; #586's CI logs at e582d20f5b (all ten failed jobs read 2026-10-30: quick test 124248739600; coverage 124248743417 and eight more, all gis.rst), #587's quick test 124288370123 (kaklise's gis.rst fix, opened 2026-10-30 20:12, passes all 18 doc files), and #582/#583's quick tests re-run 2026-10-27 (gis.rst; pandas 3.1.0 was released 2026-10-22). Found by upstream/inventory.py's check O. -->

**Review comment on #586 (COMMENT):**

Thanks for picking this up. I filed #585 and had built the same change (creation serials, rows sorted by column) to offer, so I can add some independent checks rather than a second PR.

**It fixes the run-to-run variation, on x86-64 and aarch64.** I ran every network in `examples/networks` that the issue used (Net1, Net2, Net3, Net6, ky4, ky10), plus EPANET's Net1-3, through `WNTRSimulator`. Each tree ran four times: three in fresh processes with hash and address randomisation on, and one with `PYTHONHASHSEED` fixed, ASLR off and a longer environment. On `main`, all 41 result variables of the eight networks that converge differ between runs, on Debian 13 x86-64 (EPYC 7773X) and aarch64 (Neoverse-N1). With the serial ordering, all runs were bit-identical on both. That was my branch, but it orders things the same way as yours: serials on `Var`, `Constraint` and `IfElseConstraint`, and each row sorted by column index.

**One suggestion: allocate the row vector once per `set_structure()` call.** `set_structure()` runs before every solve (724 times in a Net6 run). In my first version, as in this PR, `std::vector<...> row;` is declared inside the per-constraint loop, so it allocates once per row:
- Timed on Net6 (x86-64, one core, `main` and the change alternating), `set_structure()` took 3.85 ms per call against `main`'s 2.77 ms (three runs each).
- Declaring the vector before each loop and calling `row.clear()` per constraint brought it to 3.1 ms per call against `main`'s 2.7 ms (eight runs each). That's about 0.25% of a Net6 run.
- On Net3, where both versions take the same 183 solves, total time was the same (0.722 s against 0.730 s, means of five).

**SWIG.** I agree no wrapper change is needed. I also regenerated `evaluator_wrap.cpp` with SWIG 4.0.2 (`-c++ -python -builtin`, as `setup.py`'s `use_swig` does):
- from `main`'s sources, it reproduces the committed wrapper and `evaluator.py` byte for byte;
- from the changed header, the only additions are get/set accessors for the `serial` members.

So a later regeneration would expose `serial` to Python, unless `evaluator.i` says `%ignore` or `%immutable`.

**The CI failures look unrelated to the change:**
- **Run Coverage, the nine failing jobs (Python 3.11 to 3.13):** the unit tests pass in each (471), except one timing assertion on Windows 3.11, `test_Net6_thread_performance` ("WNTR threading took 1s longer than sequential"). Each fails one doctest, `gis.rst`: with pandas 3.1.0, which these jobs install, the floats in list cells print at display precision. The Python 3.10 jobs get pandas 2.3.3 and pass. #587, now merged, fixes it, and #582 and #583 failed the same way when re-run on 27 October.
- **Quick test (3.13, Ubuntu):** the unit tests passed (467). The run aborted in the documentation doctests, in `advancedsim.rst`'s threaded `EpanetSimulator` runs (`Fatal Python error: Aborted` with threads in `ENopen`, `ENsolveH` and the INP writer). That path doesn't use the evaluator, and the same doctest passed in #587's quick test, so it looks intermittent.

Drafted with an AI assistant (Claude), which also ran the builds and checks reported here; I read it before posting.
