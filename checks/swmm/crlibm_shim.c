/* crlibm_shim.c - the libm functions libswmm5 imports, answered by CORE-MATH
 * (correctly rounded, so the same bits on every CPU and C library).
 * (plus sincos, which gcc makes from a sin/cos pair). LD_PRELOAD it to take glibc's CPU-dispatched versions out of a run. */
double cr_acos(double), cr_asin(double), cr_atan(double), cr_cos(double),
       cr_exp(double), cr_log(double), cr_log10(double), cr_pow(double, double),
       cr_sin(double), cr_tan(double);
double acos(double x) { return cr_acos(x); }
double asin(double x) { return cr_asin(x); }
double atan(double x) { return cr_atan(x); }
double cos(double x)  { return cr_cos(x); }
double exp(double x)  { return cr_exp(x); }
double log(double x)  { return cr_log(x); }
double log10(double x){ return cr_log10(x); }
#ifdef SHIM_CANARY  /* a planted fault: a run must change, or the preload missed libswmm5 */
double pow(double x, double y) { return cr_pow(x, y) * (1 + 0x1p-20); }
#else
double pow(double x, double y) { return cr_pow(x, y); }
#endif
double sin(double x)  { return cr_sin(x); }
double tan(double x)  { return cr_tan(x); }
/* gcc merges sin(x) and cos(x) of one argument into sincos */
void sincos(double x, double *s, double *c) { *s = cr_sin(x); *c = cr_cos(x); }
