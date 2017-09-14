- exposure time = 565 s (Euclid Redbook)
- gain = 3.0
- Read out noise (ron) = 5 e- [2]
- Pixel scale = 0.1" [2]
- Diameter M1 = 1.19 m [2]
- Obscuration D2 = 0.37 m [2]
- Dark current = 0.001 e-/pixel/s [2]
- Sky Background in 550-920 nm range: 

	Version 1 [3]
		low case: 22.96 AB mag/arcsec²
		ave case: 22.35 AB mag/arcsec²
		hig case: 21.75 AB mag/arcsec²
	based on the model by Leinert+98 and Aldering+04

	Version 2 [5]
		see skybackground.py
		ave model: 22.8 mag/arcsec²

- Early Euclid-Exposure Time Calculator [4]
	S/N = F / sqrt( {F + B * A}/g + n * A * {ron/g}**2 + Dark )
		F: flux source in ADUs
		B: background
		A: area of collecting mirror
		n: number of individual exposures

------------------------------------------

# Refs

[1] Euclid Redbook

[2] arxiv:1001.0061, Euclid Science book, Table 19.1, p. 176

[3] arxiv:1001.0061, Euclid Science book, Sect 19.4, p. 176

[4] arxiv:1001.0061, Euclid Science book, Sect 21.3, p. 176

[5] Euclid Consortium meeting 2017, "Survey" (Scaramella) http://euclid2017.london/slides/Monday/Session3/SurveyStatus-Scaramella.pdf
