/* crlibm_shim_darwin.c - crlibm_shim.c for macOS: the libm functions libswmm5
 * imports, answered by CORE-MATH (correctly rounded), through dyld interposing.
 * macOS links in a two-level namespace, so a library that merely defines exp
 * is never asked; one inserted with DYLD_INSERT_LIBRARIES=/abs/path.dylib that
 * carries __DATA,__interpose pairs is, for every image in the process.
 * clang turns a sin/cos pair of one argument into __sincos_stret, and
 * pow(10, x) into __exp10(x), so those are answered too (both correctly
 * rounded, so __exp10 gives the bits cr_pow(10, x) would). -DSHIM_CANARY
 * makes pow wrong by 2^-20 relative: a planted fault, so a run that does not
 * change shows the insertion missed libswmm5.
 * crshim.sh reads the INTERPOSE lines below as the list of what is answered. */
#include <math.h>
double cr_acos(double), cr_asin(double), cr_atan(double), cr_cos(double),
       cr_exp(double), cr_log(double), cr_log10(double), cr_pow(double, double),
       cr_sin(double), cr_tan(double), cr_exp10(double);

#define INTERPOSE(mine, theirs) \
    __attribute__((used)) static const struct { const void *m, *t; } interpose_##mine \
    __attribute__((section("__DATA,__interpose"))) = { (const void *)&mine, (const void *)&theirs };

static double s_acos(double x)  { return cr_acos(x); }
static double s_asin(double x)  { return cr_asin(x); }
static double s_atan(double x)  { return cr_atan(x); }
static double s_cos(double x)   { return cr_cos(x); }
static double s_exp(double x)   { return cr_exp(x); }
static double s_log(double x)   { return cr_log(x); }
static double s_log10(double x) { return cr_log10(x); }
#ifdef SHIM_CANARY
static double s_pow(double x, double y) { return cr_pow(x, y) * (1 + 0x1p-20); }
#else
static double s_pow(double x, double y) { return cr_pow(x, y); }
#endif
static double s_sin(double x)   { return cr_sin(x); }
static double s_tan(double x)   { return cr_tan(x); }
static double s_exp10(double x) { return cr_exp10(x); }
static struct __double2 s_sincos_stret(double x)
{
    struct __double2 r;
    r.__sinval = cr_sin(x);
    r.__cosval = cr_cos(x);
    return r;
}

INTERPOSE(s_acos, acos)
INTERPOSE(s_asin, asin)
INTERPOSE(s_atan, atan)
INTERPOSE(s_cos, cos)
INTERPOSE(s_exp, exp)
INTERPOSE(s_log, log)
INTERPOSE(s_log10, log10)
INTERPOSE(s_pow, pow)
INTERPOSE(s_sin, sin)
INTERPOSE(s_tan, tan)
INTERPOSE(s_sincos_stret, __sincos_stret)
INTERPOSE(s_exp10, __exp10)
