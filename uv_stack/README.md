Script for uv-stacking.

Two versions available:
- Without weighting
- With a weighting based on a 1.1mm flux normalization

In order to use the script, you just need to introduce (see the script for an example):

- Path to where the individual pointings and associated primary beams are located
- List of IDs (string)
- List of RA (float)
- List of Dec (float)
- List of RA, Dec coordinates (string) preceded by J2000 and in hh:mm:ss dd:mm:ss
- List of fluxes (float) - If flux normalization weights applied

The script takes a list of sources RA, Dec to stack. Then, it searches for the pointings that contain the desired coordinates. After that, it performs a phase-shift for each pair of coordinates to put them at the phase center, modulo a primary beam correction (which assumes the source is small enough so a single primary beam correction for each source is applicable). Once all the pointings are phase-shifted, it concatenates them into a single MS file.
