<!-- Draft, not sent. Recipient not chosen: the report (LTH-IEA-7229, 2008) gives no contact address, and a search on 2026-10-30 did not confirm who now answers for BSM1 or for the influent files hosted at iwa-mia.org. Candidates: U. Jeppsson (Lund University, Industrial Electrical Engineering and Automation, the report's publisher) or IWA's Modelling and Integrated Assessment specialist group, which hosts the files. Find a current address before sending. Every number below is in checks/bsm1/README.md, with the commands that compute it. -->

**Subject:** BSM1 (LTH-IEA-7229): the hosted rain and storm influent files keep SI undiluted, and two smaller points

Dear BSM1 authors,

While comparing the open implementations of BSM1 (QSDsan/EXPOsan, WaterTAP and bsm2-python) with the 2008 report, I found two things in the reference itself that may be worth a note on the download page. Everything below can be recomputed from the report and the hosted files; the scripts and results are public at https://github.com/anun333/sewage/tree/main/checks/bsm1.

**1. The rain and storm files keep soluble inert COD at 30 g/m³.** In `Inf_rain_2006.txt` and `Inf_strm_2006.txt` as hosted at iwa-mia.org (2019/04), every component is diluted by the extra flow, C = C_dry·Q_dry/Q, to within 1.3e-6, except SI, which stays at 30. The report's published rain and storm results need SI diluted too:
- The influent quality index over days 7-14, computed from the files alone, gives the report's 52081.3952 for dry weather. With SI = 30·Q_dry/Q it gives 52081.3951 for rain (printed 52081.3952; a pure dilution leaves IQ unchanged) and 54061.4969 for storm (printed 54061.497). The files as hosted give 52253.8005 (+0.33%) and 54139.4000 (+0.14%).
- Effluent SI, which only flow and mixing move, comes out at 22.838 (rain) and 26.297 (storm) with SI diluted, against the printed 22.8388 and 26.2999. With the files as hosted it is 30.000 in both, and EQ rises by 1.9% and 0.95%.

So the results appear to have been computed with SI diluted, and the hosted files differ from the ones used.

**2. Appendix 4's steady state does not quite close the XI balance.** XI is inert, so at steady state its inflow Q0·XI0 = 944435.2 g/d equals its outflow Qe·XIe + Qw·XIu. With Appendix 4's values the outflow is 944429.43 g/d, short by 6.1e-6 (relative). The Simulink 200-day values close the same balance to 4e-10. The converged implementations we ran sit at the balanced values, 1e-6 to 1.3e-5 away from Appendix 4 in the particulates. The report calls these the values "after 100 days", which would fit a start some way from steady state; that is our inference, not checked.

**3. Smaller points,** in case an errata list is kept:
- Table 6 prints reactor 2's TSS as 3282, where Appendix 4's 3282.5339 rounds to 3283.
- Table 8 labels the effluent nitrate SNO,u and gives oxygen in g COD/m³.
- Appendix 2's FORTRAN column gives an effluent flow of 18055.2 against Matlab's 18061.33. Since the flow is Q0 - Qw, the FORTRAN figures seem to have been averaged differently.
- Section 5.1 limits KLa5 to 0-10 1/h (240 1/d), but Appendix 5's dry-weather KLa5 spans 242.2831 1/d.
- Appendix 3 gives the nitrate controller's Tt as 1.015 d, where Appendix 5 gives 0.015 d.

Thank you for BSM1 and for keeping the report and files available. It's what makes a comparison like this possible.

Best regards,
anun333 (https://github.com/anun333)

Drafted with an AI assistant (Claude), which also ran the checks reported here; I read it before sending.
