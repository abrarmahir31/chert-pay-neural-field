"""Synthetic benchmark with known true parameters.

Wells are scattered over an area like the study area. Rock-physics parameters (m, n, f_micro)
are smooth spatial fields; rock properties (phi, Sw, Vsh, mineral fractions) vary sample by
sample with vertical correlation. Curves are produced by the forward models in
`chertfield.physics.forward`, then noise, per-well nuisance terms and missing-curve masks that
mimic the real coverage are applied. Everything is driven by one seed.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np
import torch

from chertfield.physics import forward as fw


@dataclass
class SynthConfig:
    n_wells: int = 60
    n_samples: int = 200            # samples per well (0.5 ft step -> 100 ft)
    extent_km: tuple = (57.0, 52.0)
    seed: int = 0
    # spatial fields: (mean, half-range, correlation length km)
    m_field: tuple = (2.1, 0.35, 15.0)
    n_field: tuple = (1.9, 0.25, 20.0)
    fmic_field: tuple = (0.35, 0.25, 12.0)
    rw: float = 0.045               # ohm.m at reservoir temperature (constant)
    rmf: float = 0.25               # median mud-filtrate resistivity; true value varies per well
    rmf_spread: float = 0.30        # log-normal sigma of the true per-well Rmf
    rmf_header_error: float = 0.15  # log-normal sigma of the error of the Rmf known to the model
    sxo_exp_range: tuple = (0.12, 0.30)  # per-well flushing exponent k in Sxo = Sw^k (unknown to model)
    frac_wet_wells: float = 0.25    # wells with no hydrocarbon column
    noise: dict = None              # per-curve noise std
    p_missing: dict = None          # probability a well lacks the curve
    nphi_offset_std: float = 0.01   # per-well neutron nuisance (matrix convention / calibration)
    rhob_offset_std: float = 0.01
    forward_resistivity: str = "dual_porosity"

    def __post_init__(self):
        if self.noise is None:
            self.noise = dict(RHOB=0.015, NPHI=0.01, GR=4.0, LRT=0.03, LRXO=0.05, DT=1.5, PE=0.15)
        if self.p_missing is None:
            # from results/audit/audit_summary.json: DT 124/625, PE 259/625, shallow 594/625
            self.p_missing = dict(DT=0.80, PE=0.59, LRXO=0.05)


def _smooth_field(rng, xy, mean, half_range, corr_km, n_modes=24):
    """Smooth random field from random cosine modes, squashed into mean +/- half_range."""
    k = rng.normal(0.0, 1.0 / corr_km, size=(n_modes, 2))
    ph = rng.uniform(0, 2 * np.pi, n_modes)
    amp = rng.normal(0, 1, n_modes) / np.sqrt(n_modes / 2)
    z = (amp * np.cos(xy @ k.T + ph)).sum(1)
    return mean + half_range * np.tanh(z)


def _ar1(rng, n_wells, n, rho, scale):
    e = rng.normal(0, scale * np.sqrt(1 - rho**2), size=(n_wells, n))
    x = np.zeros((n_wells, n))
    x[:, 0] = rng.normal(0, scale, n_wells)
    for i in range(1, n):
        x[:, i] = rho * x[:, i - 1] + e[:, i]
    return x


def _sigmoid(x):
    return 1.0 / (1.0 + np.exp(-x))


def make_benchmark(cfg: SynthConfig | None = None) -> dict:
    """Return dict of numpy arrays: observed curves, masks, coordinates and the truth."""
    cfg = cfg or SynthConfig()
    rng = np.random.default_rng(cfg.seed)
    W, N = cfg.n_wells, cfg.n_samples
    xy = rng.uniform(0, 1, size=(W, 2)) * np.asarray(cfg.extent_km)
    m_w = _smooth_field(rng, xy, *cfg.m_field)
    n_w = _smooth_field(rng, xy, *cfg.n_field)
    f_w = np.clip(_smooth_field(rng, xy, *cfg.fmic_field), 0.02, 0.9)
    z = np.tile(np.arange(N) * 0.5, (W, 1))                       # ft below top

    # rock properties, vertically correlated
    phi = np.clip(0.04 + 0.38 * _sigmoid(_ar1(rng, W, N, 0.97, 1.2) - 0.3 - z / 80.0), 0.02, 0.5)
    vsh = np.clip(0.25 * _sigmoid(_ar1(rng, W, N, 0.95, 1.5) - 1.5), 0.0, 0.4) * (1 - phi)
    solid = 1.0 - phi - vsh
    w_q = _sigmoid(_ar1(rng, W, N, 0.98, 1.5) + 1.0 - z / 60.0)   # chert-rich at the top
    w_d = 0.3 * _sigmoid(_ar1(rng, W, N, 0.98, 1.5) - 1.0) * (1 - w_q)
    v_qtz, v_dol = solid * w_q, solid * w_d
    v_cal = solid - v_qtz - v_dol

    # fluids: hydrocarbon column above a per-well contact; wet wells have none
    wet = rng.uniform(size=W) < cfg.frac_wet_wells
    contact = np.where(wet, -1.0, rng.uniform(20, 90, W))[:, None]
    trans = _sigmoid((z - contact) / 6.0)                         # 0 in pay, 1 below contact
    sw_irr_mac = np.clip(0.10 + 0.04 / np.maximum(phi, 0.03), 0.1, 1.0)
    sw_mac = np.clip(sw_irr_mac + (1 - sw_irr_mac) * trans, 0.02, 1.0)
    sw_mac = np.where(wet[:, None], 1.0, sw_mac)
    k_w = rng.uniform(*cfg.sxo_exp_range, W)
    sxo_mac = sw_mac ** k_w[:, None]                              # flushing by mud filtrate
    rmf_w = cfg.rmf * np.exp(rng.normal(0, cfg.rmf_spread, W))
    rmf_obs = rmf_w * np.exp(rng.normal(0, cfg.rmf_header_error, W))

    T = lambda a: torch.as_tensor(a, dtype=torch.float64)  # noqa: E731
    mT, nT, fT = (T(a)[:, None] for a in (m_w, n_w, f_w))
    args = [T(a) for a in (phi, vsh, v_qtz, v_cal, v_dol)]
    sxo_tot = fw.total_sw(T(sxo_mac), fT)
    rhob = fw.bulk_density(*args, sxo_tot)
    nphi = fw.neutron_porosity(*args, sxo_tot)
    pe = fw.photoelectric(*args, rhob)
    dt = fw.sonic_raymer(*args)
    gr_clean, gr_sh = rng.uniform(10, 25, (W, 1)), rng.uniform(90, 140, (W, 1))
    gr = fw.gamma_ray(T(vsh) / 0.4, T(gr_clean), T(gr_sh))
    if cfg.forward_resistivity == "dual_porosity":
        lrt = fw.log10_rt_dual_porosity(T(phi), T(sw_mac), fT, mT, nT, cfg.rw, vsh=T(vsh))
        lrxo = fw.log10_rt_dual_porosity(T(phi), T(sxo_mac), fT, mT, nT, T(rmf_w)[:, None], vsh=T(vsh))
    else:
        lrt = fw.log10_rt_archie(T(phi), T(sw_mac), mT, nT, cfg.rw)
        lrxo = fw.log10_rt_archie(T(phi), T(sxo_mac), mT, nT, T(rmf_w)[:, None])

    clean = dict(RHOB=rhob, NPHI=nphi, GR=gr, LRT=lrt, LRXO=lrxo, DT=dt, PE=pe)
    nphi_off = rng.normal(0, cfg.nphi_offset_std, (W, 1))
    rhob_off = rng.normal(0, cfg.rhob_offset_std, (W, 1))
    obs, mask = {}, {}
    for k, v in clean.items():
        o = v.numpy() + rng.normal(0, cfg.noise[k], (W, N))
        if k == "NPHI":
            o = o + nphi_off
        if k == "RHOB":
            o = o + rhob_off
        present = rng.uniform(size=W) >= cfg.p_missing.get(k, 0.0)
        mask[k] = np.repeat(present[:, None], N, axis=1)
        obs[k] = np.where(mask[k], o, np.nan)
    truth = dict(m=m_w, n=n_w, f_micro=f_w, phi=phi, vsh=vsh, v_qtz=v_qtz, v_cal=v_cal,
                 v_dol=v_dol, sw_macro=sw_mac, sxo_macro=sxo_mac,
                 sw_total=fw.total_sw(T(sw_mac), fT).numpy(),
                 bvh=fw.bulk_volume_hydrocarbon(T(phi), T(sw_mac), fT).numpy(),
                 wet_well=wet, contact_ft=contact[:, 0], nphi_offset=nphi_off[:, 0],
                 rhob_offset=rhob_off[:, 0], sxo_exp=k_w, rmf=rmf_w, gr_clean=gr_clean[:, 0],
                 gr_shale=gr_sh[:, 0])
    return dict(xy_km=xy, z_ft=z, rmf_obs=rmf_obs, obs=obs, mask=mask, truth=truth,
                clean={k: v.numpy() for k, v in clean.items()}, config=asdict(cfg))
