import numpy as np

import astropy.units as u
import astropy.constants as c


# With correction factor, per arcsec2:
#mdb_zodi = 1.71 * 1.5e-18 * u.erg * u.cm**-2 * u.s**-1 * u.angstrom**-1  # erg/cm2/s  A-1
mdb_zodi = 2.5e-18 * u.erg * u.cm**-2 * u.s**-1 * u.angstrom**-1  # erg/cm2/s  A-1

# At 7000 angstrom:
Hz_per_angstrom = 61173395229.1875 * u.Hz / u.angstrom

mdb_zodi_per_hz = mdb_zodi / Hz_per_angstrom


mdb_zodi_jansky = mdb_zodi_per_hz.to(u.Jansky)


mag_per_arcsec2 = -2.5 * np.log10(mdb_zodi_jansky.value) + 8.9

print "Mag AB of sky per arcsec2: ", mag_per_arcsec2



