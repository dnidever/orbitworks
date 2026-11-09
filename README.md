# ASTR 372 — Orbit Works

## Run

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

Keep `app.py`, `orbit.py`, and `orbit.pkl` in the same directory. The app uses the original course orbit calculation and observational data. It does not disclose the injected parameters for the two unknown systems.

## Sections

1. Explore stellar and planetary radial velocities with interactive controls.
2. Compare Earth-like, Jupiter-like, and hot-Jupiter signals.
3. Fit the two unknown observational datasets with parameter sliders and residual plots.

## Notes

The uploaded `orbit.py` uses a one-period orbit template. The app repeats this template periodically for display over the observational baseline. The fitted model has a fixed phase and systemic velocity, consistent with the provided synthetic datasets. The course numerical routine is retained unchanged.