<!-- DRAFT for pyswmm/Stormwater-Management-Model. Not posted; reviewed before posting. -->

**Title:** The `.out` header's start date is one report step early in about a third of runs where REPORT_START is a whole number of steps after START

`output_open()` writes the reporting start date into the `.out` header (`src/solver/output.c:394` on `develop`; `output.c:387` in USEPA's tree):

```c
z = (double)ReportStep/86400.0;
if ( StartDateTime + z > ReportStart ) z = StartDateTime;
else
{
    z = floor((ReportStart - StartDateTime)/z) - 1.0;
    z = StartDateTime + z*(double)ReportStep/86400.0;
}
```

When REPORT_START is a whole number of report steps after START, `(ReportStart - StartDateTime)/z` should be an integer. Both dates are binary day counts, though, so the quotient often comes out just below it, and `floor()` then drops a step. The header date is then one report step early.

**Example.** START 01/07/2028 16:00, REPORT_START 01/08/2028 15:50, REPORT_STEP 00:10:00. The header holds 15:30, so header + one step gives 15:40, while the first period's own stored date is 15:50. With REPORT_START at 15:40, 16:00 or 16:10, it comes out right.

**How often.** I swept SWMM's date encoding in Python (`datetime_encodeDate` plus `datetime_encodeTime`). Starts were in 1990-2030, report steps from 1 minute to 1 day, and REPORT_START 1 to 2000 steps after START:
- 33,953 of 100,145 aligned cases were one step early, about a third;
- the rate depends on the mix of steps and dates.

A reader that relies on the header, such as `SMO_getStartDate()` plus the report step in swmm-output and the tools built on it, labels every period one step early. The per-period dates stored in the file are right.

**A fix.** This is the same 1 ms tolerance that `getDateTime()` already uses (`swmm5.c`, `datetime_addSeconds(StartDateTime, (elapsedMsec+1)/1000.0)`) and that the `TotalDuration` fix in USEPA/Stormwater-Management-Model#237 uses:

```c
z = floor(((ReportStart - StartDateTime)*SECperDAY + 0.001) / ReportStep) - 1.0;
z = StartDateTime + z*(double)ReportStep/SECperDAY;
```

In the same Python model:
- it gives the right date in all 100,145 aligned cases;
- it changes none of 199,337 cases where REPORT_START is not a whole number of steps after START (whole-second offsets).

I haven't built and run it in SWMM. The example above was confirmed with a real run of USEPA `develop`, where the header said 15:30 and the first period 15:50.

Related: USEPA/Stormwater-Management-Model#152 and #237, the same `floor()` of a day difference in `project.c`.

Drafted with an AI assistant (Claude), which also ran the builds and checks reported here; I read it before posting.
