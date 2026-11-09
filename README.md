# 🪐 Orbit Works

**Interactive orbital mechanics and exoplanet radial-velocity fitting** for ASTR 372 Stellar Astrophysics at Montana State University.

## Launch locally

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

For deployment on [Streamlit Community Cloud](https://share.streamlit.io/), select this GitHub repository, the `main` branch, and entry point `app.py`.

## Activities

1. **Explore orbits:** Adjust stellar mass, planet mass, orbital period, and eccentricity and view the stellar radial-velocity curve.
2. **Compare systems:** Compare Earth-like, Jupiter-like, and hot-Jupiter radial-velocity amplitudes.
3. **Fit unknown planets:** Fit two sets of simulated stellar radial-velocity measurements, inspect residuals, and download fitted parameters.

## Files

- `app.py`: Streamlit user interface
- `orbit.py`: Original course orbit calculations, adapted from Carroll & Ostlie
- `orbit_data.b85`: Compact encoding of the two provided `orbit.pkl` observation sets (200 observations each). Times are preserved to 0.1 microsecond and radial velocities to 0.00001 m/s, more than sufficient for this exercise
- `requirements.txt`: Python dependencies

The original local `orbit.pkl` file remains the archival source. The app uses `orbit_data.b85` for text-based GitHub deployment. The numerical model assumes an edge-on orbital inclination and fixed phase/orientation; the unknown systems' injected parameters are not displayed in the student interface.
