# Image

- exposure time = 565 s [1, 6]
- gain = 3.1 e-/DN [8]
- Read out noise (ron) = 4.2 e- [7]
- Pixel scale = 0.1" [5]
- Pixel size = 12 um x 12um [6]
- Diameter M1 = 1.20 m [5]
- Diameter D2 = 0.35 m [5]
- Dark current = 0.00056 e-/pixel/s (less than 2 e-/px/hr) [6]
- Passband = 550-900 nm [5]
- Zero point = 25.5 AB [10]
- Sky Background in 550-920 nm range: 

	Version 1 [2]

		low case: 22.96 AB mag/arcsec²

		ave case: 22.35 AB mag/arcsec²

		hig case: 21.75 AB mag/arcsec²

	based on the model by Leinert+98 and Aldering+04

	Version 2 [4]

		see skybackground.py

		ave model: 22.8 mag/arcsec²

- Early Euclid-Exposure Time Calculator [3]

		S/N = F / sqrt( {F + B * A}/g + n * A * {ron/g}**2 + Dark )

		F: flux source in ADUs

		B: background

		A: area of collecting mirror

		n: number of individual exposures

- Sensitivity [7]
		m(AB)>24.5 at 10 s in 3 exposures for galaxy size 0.3 arcsec

- System PSF size [7]
		<0.18 arcsec full width half maximum at 800 nm

- System PSF ellipticity [7]
		≤15% using a quadrupole definition

# Galaxy parameters

Catalogues with

		position, flux, half-light radius, Sersic index, ellipticity

only consider gal mag fainter than 20

for 20 < m < 25, galaxy counts power law of slope ~0.36 > 

radius drawn from skewed normal distribution, with <log10 rh/arcsec> and sigma(log10 rh) depending on magnitude

Single Sersic profiles (index drawn from a lognormal, between 0.3 and 4.5), does not depend on any other param

ellipticities drawn from Rayleigh distribution, does not depend on any other param

------------------------------------------

# Refs

[1] Euclid Redbook

[2] arxiv:1001.0061, Euclid Science book, Sect 19.4

[3] arxiv:1001.0061, Euclid Science book, Sect 21.3

[4] Euclid Consortium meeting 2017, "Survey" (Scaramella) http://euclid2017.london/slides/Monday/Session3/SurveyStatus-Scaramella.pdf

[5] arxiv:1610.05508, The Euclid mission design, Racca+

[6] https://www.e2v.com/content/uploads/2017/08/ProcSPIE_Euclid.pdf, Charge-Coupled Devices for the ESA Euclid M-class Mission, Endicott+

[7] arxiv:1608.08603, VIS: the visible imager for Euclid Cropper+

[8] https://doi.org/10.1007/s10686-015-9440-7, Niemi+2015, Measuring a charge-coupled device point spread function, Experimental Astronomy

[9] arxiv:1609.03281, A study of the sensitivity of shape measurements to the input parameters of weak lensing image simulations, Hoekstra+

[10] http://iopscience.iop.org/article/10.1088/0004-637X/811/1/20/meta (Supplementary material) Collett, 2015

