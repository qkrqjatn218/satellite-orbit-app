# /project/source/OP.py
import sys, os
sys.path.append(os.path.dirname(__file__))

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from orbit_determination.model import Satrec
from orbit_determination.conveniences import jday_datetime
from datetime import datetime, timedelta
from astropy.time import Time
from astropy.coordinates import TEME, GCRS
from astropy import units as u
from astropy.coordinates import CartesianRepresentation, CartesianDifferential
from astropy.coordinates import ITRS

def SGP4propagate(start_datetime, duration_minutes, timestep, tle_line1, tle_line2, frame):
    satellite = Satrec.twoline2rv(tle_line1, tle_line2)
    
    steps = int((duration_minutes * 60) / timestep)
    time_list = [start_datetime + timedelta(seconds=i * timestep) for i in range(steps)]

    orbit_data = []

    for minute in time_list:
        jd, fr = jday_datetime(minute)
        e, r, v = satellite.sgp4(jd, fr) 
        if e != 0:
            print(f"Propagation error at {minute} (code {e})")
            continue

        t = Time(minute, scale='utc')
        r_teme = np.array(r, dtype=float).reshape(3) * u.km
        v_teme = np.array(v, dtype=float).reshape(3) * u.km / u.s

        if frame == "TEME":
            orbit_data.append({
                'datetime': minute,
                'x_km': r_teme[0].value,
                'y_km': r_teme[1].value,
                'z_km': r_teme[2].value,
                'vx_kms': v_teme[0].value,
                'vy_kms': v_teme[1].value,
                'vz_kms': v_teme[2].value
            })

        elif frame in ["GCRS", "ITRS"]:
            r_cart = CartesianRepresentation(r_teme)
            v_diff = CartesianDifferential(v_teme)
            r_full = r_cart.with_differentials(v_diff)

            teme_coord = TEME(r_full, obstime=t)
            gcrs_coord = teme_coord.transform_to(GCRS(obstime=t))

            if frame == "GCRS":
                pos = gcrs_coord.cartesian.xyz.to_value(u.km)
                vel = gcrs_coord.velocity.d_xyz.to_value(u.km/u.s)

            elif frame == "ITRS":
                itrs_coord = gcrs_coord.transform_to(ITRS(obstime=t))
                pos = itrs_coord.cartesian.xyz.to_value(u.km)
                vel = itrs_coord.velocity.d_xyz.to_value(u.km/u.s)

            orbit_data.append({
                'datetime': minute,
                'x_km': pos[0],
                'y_km': pos[1],
                'z_km': pos[2],
                'vx_kms': vel[0],
                'vy_kms': vel[1],
                'vz_kms': vel[2]
            })

        else:
            raise ValueError(f"지원하지 않는 좌표계: {frame}")

    return orbit_data



