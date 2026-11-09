"""Orbit Works: ASTR 372 interactive orbital mechanics and radial-velocity fitting."""
from pathlib import Path
import io
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from orbit import orbit

st.set_page_config(page_title="Orbit Works | ASTR 372", page_icon="🪐", layout="wide")
st.title("🪐 Orbit Works")
st.caption("ASTR 372 · Stellar Astrophysics · Montana State University")
DAY = 86400.0
ROOT = Path(__file__).resolve().parent

@st.cache_data(show_spinner=False)
def compute_orbit(mstar, mplanet, period, ecc):
    return orbit(float(mstar), float(mplanet), float(period), float(ecc), n=2500)

@st.cache_data(show_spinner=False)
def observations():
    """Load both original observation series, stored as compact text for GitHub."""
    import base64
    import json
    import zlib
    encoded = (ROOT / "orbit_data.b85").read_text().strip()
    raw = zlib.decompress(base64.b85decode(encoded))
    arrays = json.loads(raw)
    return tuple({"t": np.asarray(d, float)[:, 0], "rv": np.asarray(d, float)[:, 1]} for d in arrays)

def rv_model(star, times, period_days):
    phase = np.mod(np.asarray(times) / DAY, period_days)
    t = star["t"] / DAY
    valid = np.isfinite(t) & np.isfinite(star["rv"])
    return np.interp(phase, t[valid], star["rv"][valid])

def draw_curve(ax, star, planet=None):
    ax.plot(star["t"] / DAY, star["rv"], label="Star", lw=2)
    if planet is not None:
        ax.plot(planet["t"] / DAY, planet["rv"], label="Planet", lw=1.5)
    ax.set(xlabel="Time (days)", ylabel="Radial velocity (m/s)")
    ax.grid(alpha=.25)
    ax.legend()

section = st.sidebar.radio("Activity", ["1 · Explore orbits", "2 · Compare systems", "3 · Fit unknown planets"])
st.sidebar.markdown("**ASTR 372 · Stellar Astrophysics**")
st.sidebar.caption("Uses the course orbit.py model, assuming edge-on orbits.")

if section.startswith("1"):
    st.header("Explore stellar and planetary radial velocities")
    st.markdown("A planet and its star orbit their common center of mass. The planet moves faster, but the stellar wobble is what radial-velocity surveys measure.")
    c1, c2 = st.columns(2)
    with c1:
        ms = st.slider("Stellar mass (solar masses)", 0.2, 3.0, 1.0, 0.1)
        mp = st.slider("Planet mass (Earth masses)", 0.1, 1500.0, 1.0, 0.1)
    with c2:
        per = st.slider("Orbital period (days)", 2.0, 2000.0, 365.0, 1.0)
        ecc = st.slider("Eccentricity", 0.0, 0.85, 0.0, 0.05)
    star, planet = compute_orbit(ms, mp, per, ecc)
    peak = float(np.max(np.abs(star["rv"])))
    a = ((6.673e-11 * (ms * 1.9891e30 + mp * 5.9736e24) * (per * DAY)**2) / (4 * np.pi**2))**(1/3) / 1.4959787066e11
    a1, a2, a3 = st.columns(3)
    a1.metric("Maximum |stellar RV|", f"{peak:.3g} m/s")
    a2.metric("Orbital period", f"{per:g} days")
    a3.metric("Semimajor axis", f"{a:.3g} AU")
    show_planet = st.checkbox("Show planetary radial velocity too", value=False)
    fig, ax = plt.subplots(figsize=(9,4.5))
    draw_curve(ax, star, planet if show_planet else None)
    st.pyplot(fig)
    plt.close(fig)
    with st.expander("Questions to consider"):
        st.markdown("1. How does the stellar velocity change when you increase planet mass?\n2. What happens when the orbital period becomes shorter?\n3. How does eccentricity change the *shape* of the curve?\n4. Why is the stellar signal much smaller than the planetary signal?")

elif section.startswith("2"):
    st.header("Compare planetary systems")
    st.markdown("All three examples have a 1-solar-mass star and a circular orbit. Compare stellar radial-velocity amplitudes and consider detectability with **1 m/s precision**.")
    systems = [("Earth-like: 1 M⊕, 1 year", 1., 365.), ("Jupiter-like: 318 M⊕, 5 years", 318., 5*365.), ("Hot Jupiter: 318 M⊕, 4 days", 318., 4.)]
    selected = st.multiselect("Systems to display", [x[0] for x in systems], default=[x[0] for x in systems])
    use_phase = st.toggle("Normalize time by orbital period (phase)", value=True)
    fig, ax = plt.subplots(figsize=(9,4.8))
    for name, mass, period in systems:
        if name not in selected:
            continue
        star, _ = compute_orbit(1., mass, period, 0.)
        xx = star["t"] / (period * DAY) if use_phase else star["t"] / DAY
        ax.plot(xx, star["rv"], label=name, lw=2)
    ax.set(xlabel="Orbital phase (cycles)" if use_phase else "Time (days)", ylabel="Stellar radial velocity (m/s)")
    ax.grid(alpha=.25)
    if selected:
        ax.legend()
    st.pyplot(fig)
    plt.close(fig)
    if st.checkbox("Show peak radial-velocity amplitudes"):
        for name, mass, period in systems:
            star, _ = compute_orbit(1., mass, period, 0.)
            st.write(f"**{name}:** {np.max(np.abs(star['rv'])):.3g} m/s")
    st.text_area("Which systems could you detect at 1 m/s precision? Explain your reasoning.", key="comparison_answer")

else:
    st.header("Fit the orbit of an unknown planet")
    st.markdown("Adjust the planet mass, period, and eccentricity until the model curve matches the measured radial velocities. The stellar mass is **1 M☉**; the app does not reveal the best-fit parameters.")
    try:
        datasets = observations()
    except Exception as exc:
        st.error(f"Unable to load orbit.pkl: {exc}")
        st.stop()
    dataset_id = st.radio("Observation set", [1, 2], horizontal=True)
    obs = datasets[dataset_id - 1]
    times = np.asarray(obs["t"], float)
    values = np.asarray(obs["rv"], float)
    c1, c2, c3 = st.columns(3)
    with c1:
        mass = st.slider("Planet mass (Earth masses)", 1, 2000, 100 if dataset_id == 1 else 500, 1, key=f"mass{dataset_id}")
    with c2:
        period = st.slider("Period (days)", 5, 250, 80 if dataset_id == 1 else 70, 1, key=f"period{dataset_id}")
    with c3:
        ecc = st.slider("Eccentricity", 0., 0.85, 0.1, 0.01, key=f"ecc{dataset_id}")
    star, _ = compute_orbit(1., mass, period, ecc)
    model = rv_model(star, times, period)
    residuals = values - model
    rms = np.sqrt(np.mean(residuals**2))
    show_residuals = st.checkbox("Show residuals", value=True)
    show_rms = st.checkbox("Show numerical RMS of residuals", value=False)
    if show_rms:
        st.metric("RMS of data − model", f"{rms:.2f} m/s")
    fig, axes = plt.subplots(2 if show_residuals else 1, 1, figsize=(9, 6 if show_residuals else 4.5), sharex=show_residuals, gridspec_kw={"height_ratios":[3,1]} if show_residuals else None)
    if not show_residuals:
        axes = [axes]
    ax = axes[0]
    ax.scatter(times / DAY, values, s=20, alpha=.75, label="Observations")
    grid = np.linspace(0, max(np.max(times) / DAY, period), 1500)
    ax.plot(grid, rv_model(star, grid * DAY, period), color="tab:red", lw=2, label="Model")
    ax.set_ylabel("Stellar RV (m/s)")
    ax.grid(alpha=.25)
    ax.legend()
    if show_residuals:
        axes[1].scatter(times / DAY, residuals, s=16)
        axes[1].axhline(0, color="tab:red", lw=1)
        axes[1].set_ylabel("Residual (m/s)")
        axes[1].grid(alpha=.25)
    axes[-1].set_xlabel("Time (days)")
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)
    with st.expander("Fitting tips and questions"):
        st.markdown("**Period:** Match the spacing of repeating peaks and troughs.\n\n**Mass:** Match the velocity amplitude.\n\n**Eccentricity:** Match deviations from a sinusoidal curve.\n\n**Reflection:** Which parameter was easiest to constrain? How does measurement noise affect your confidence?")
    st.text_area("Record your estimated mass, period, eccentricity, and reasoning:", key=f"notes{dataset_id}")
    st.download_button("Download my current parameter estimates (CSV)", data=f"dataset,stellar_mass_solar,planet_mass_earth,period_days,eccentricity,rms_m_per_s\n{dataset_id},1,{mass},{period},{ecc},{rms:.6g}\n", file_name=f"astro372_orbit_fit_{dataset_id}.csv", mime="text/csv")

st.divider()
st.caption("Orbit model adapted from Carroll & Ostlie; assumes edge-on viewing and fixed orbital orientation. Real fits may also require inclination, phase, systemic velocity, and uncertainties.")
