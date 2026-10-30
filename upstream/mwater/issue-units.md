<!-- Draft, not posted. Checked 2026-10-30 against mWater/asset-standards main at c676752 (water/units.csv, sanitation/units.csv, VERIFICATION-REPORT.md S6-S11, REVIEW-NEEDED.md) and NIST SP 811 (2008 edition, Appendix B; sha256 788dd8f0...). Exact values computed with rational arithmetic from the definitions (ft = 0.3048 m, US survey ft = 1200/3937 m, US gal = 231 in³ = 3.785411784 L, lb = 0.45359237 kg, g_n = 9.80665 m/s², water at 4 °C = 999.972 kg/m³). -->

**Title:** Table 2 (units): three more points for the erratum (water-column pressures, the acre-foot's basis, horsepower)

`REVIEW-NEEDED.md` says mWater is deciding whether to post an erratum for Table 2. I checked every conversion factor in both `units.csv` files against exact definitions and NIST SP 811 (2008, Appendix B). I confirm S6, S7 and S9 in `VERIFICATION-REPORT.md`, and the table at the end gives exact values for those rows. Three points are not in the report, and one of them affects how S8 is corrected.

**1. `m H₂O` and `cm H₂O` are labelled 4 °C but carry the conventional values, while `ft H₂O` and `in H₂O` carry true 4 °C values.**
- The tables give "meters of water (4 °C)" = 9806.65 and "centimeters of water (4 °C)" = 98.0665. These are the conventional units (ρ = 1000 kg/m³ × g_n). NIST SP 811 lists "centimeter of water (4 ºC)" as 9.806 38 E+01 Pa and "centimeter of water, conventional (cmH2O)" as 9.806 65 E+01.
- "feet of water (39.2 °F)" = 2988.98 and "inches of water (39.2 °F)" = 249.082 are SP 811's values at 39.2 °F, which is 4 °C. The conventional values are 2989.067 and 249.0889.
- So within one table, a foot of water is 2988.98/0.3048 = 9806.36 Pa per metre and a metre of water is 9806.65 Pa. They differ by 2.9e-5. The fix is either to relabel the two metric rows "conventional", or to use 9806.38 and 98.0638.

**2. The acre-foot's correct value depends on which foot the table uses.**
- S8 says the correct figure is 1233.489 m³. That is the acre-foot based on the U.S. survey foot: SP 811 lists "acre foot (based on U.S. survey foot)" as 1.233 489 E+03 m³.
- But the same tables use the international foot everywhere else: `ft` = 0.3048, `ft²` = 0.09290304, `ft³` = 0.02831685, and in the sanitation table `acre` = 4046.8564, the international acre (the survey acre is 4046.873).
- With the international foot, an acre-foot is 43560 × 0.3048³ = 1233.48183754752 m³, so **1233.482**.
- The U.S. survey foot was retired at the end of 2022 (NIST and NOAA, Federal Register 85 FR 62698, 2020-10-05). So 1233.482 matches both the rest of the table and current U.S. practice. `REVIEW-NEEDED.md`'s "1233.48" fits either value.

**3. `hp` = 746 is the electric horsepower.**
- SP 811 lists horsepower (550 ft·lbf/s) = 745.6999 W, horsepower (electric) = 746 W exactly, and horsepower (metric) = 735.4988 W.
- The tables call 746 "horsepower; System: US". For pump and motor nameplates, where "hp" usually means 550 ft·lbf/s, that is 0.04% high.
- Relabelling the row "horsepower (electric)", or using 745.6999, would remove the ambiguity.

**Exact values for the rows S6, S7, S9 and the points above concern** (base unit as in Table 2; "now" is as published in water / sanitation):

| Unit | Now | Exact | Note |
| --- | --- | --- | --- |
| m³/d | 8.64 X 10⁴ | 1.157407 × 10⁻⁵ (1/86400) | S6 |
| m³/hr | 3600 (san.) | 2.777778 × 10⁻⁴ (1/3600) | S6 |
| L/min | 60 (san.) | 1.666667 × 10⁻⁵ | S6 |
| L/d | 86.4 | 1.157407 × 10⁻⁸ | S6 |
| ML/d | 8.64 X 10⁷ | 1.157407 × 10⁻² | S6 |
| gal/min | 6.30902 X 10⁻⁵ / 6.30902 X 10⁵ | 6.309020 × 10⁻⁵ | S7: the water value is right |
| gal/d | 4.38126 X 10⁻⁸ / 4.38126 X 10⁸ | 4.381264 × 10⁻⁸ | S7: the water value is right |
| Mgal | 3785 | 3785.412 | S9 |
| acre-ft | 1223.489 | 1233.482 (international foot); 1233.489 (U.S. survey foot) | S8, point 2 |
| m H₂O (4 °C) | 9806.65 | 9806.38 at 4 °C; 9806.65 conventional | point 1 |
| cm H₂O (4 °C) | 98.0665 | 98.0638 at 4 °C; 98.0665 conventional | point 1 |
| hp | 746 | 745.6999 (550 ft·lbf/s); 746 (electric) | point 3 |

Every other factor in both tables agrees with its definition to the digits given, including `psi` (6894.757293), `in Hg (32 °F)`, `mm Hg` (133.322387), `lb/d`, `ft²`, `acre`, `gal`, `Mgal/d` and the Gregorian `mo` and `yr`.

**Effect on data already collected:** none on values recorded in their original units. The factors matter only where software converts with them:
- the flow-rate rows (S6, S7) would give wrong numbers by orders of magnitude;
- the published acre-foot (S8) is 0.8% low;
- `Mgal` (S9) is 0.011% low;
- the three points above are below 0.05%.

The script that computes the exact column is short, and I can add it to `tools/` as a check if that's useful.

Drafted with an AI assistant (Claude), which also ran the checks reported here; I read it before posting.
