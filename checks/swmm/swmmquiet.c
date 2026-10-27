/* swmmquiet.c - run one SWMM model through libswmm5 with no timing output,
 * so crnumerics' repro-diff can compare runs: runswmm prints elapsed time,
 * swmm_run prints only its (deterministic) progress lines.
 *   swmmquiet INP RPT OUT   -> exit status = SWMM error code */
#include "swmm5.h"
int main(int argc, char **argv)
{
    if (argc != 4) return 2;
    return swmm_run(argv[1], argv[2], argv[3]);
}
