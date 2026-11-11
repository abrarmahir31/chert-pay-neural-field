"""Differentiable tool-response (forward) models.

All functions take and return torch tensors, broadcast freely, and are smooth in their inputs.

Volumetric model per sample (bulk-volume fractions, sum to 1):
    phi (total porosity) + vsh (shale) + v_qtz (chert/quartz) + v_cal (calcite) + v_dol (dolomite)

ASSUMPTIONS (deliberate simplifications; see docs/forward_models.md):
  * Curves are used as delivered by the logging contractor. No borehole, mud-cake, invasion or
    temperature corrections are applied here; unknown corrections are represented by per-well
    nuisance offsets/gains (see `apply_nuisance`) and tested by sensitivity analysis.
  * Density and neutron read the flushed zone (fluid = mud filtrate + residual hydrocarbon).
  * Neutron response is LINEAR in volumes, in limestone porosity units. Real tool responses
    are non-linear in dolomite and sandstone; the matrix-convention error is absorbed by a
    per-well neutron offset.
  * Deep resistivity reads the uninvaded zone (Rw, Sw); shallow resistivity the flushed zone
    (Rmf, Sxo). No shoulder-bed or invasion modelling.
End-point constants are textbook values and are configuration, not learned (unless stated).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import torch

EPS = 1e-6


@dataclass
class EndPoints:
    """Mineral and fluid end-points (textbook values; g/cc, limestone p.u., us/ft, barns/cc)."""

    rho: dict = field(default_factory=lambda: dict(qtz=2.65, cal=2.71, dol=2.87, sh=2.55,
                                                   mf=1.05, hc=0.80))
    # neutron response in limestone porosity units (fraction)
    nphi: dict = field(default_factory=lambda: dict(qtz=-0.02, cal=0.0, dol=0.02, sh=0.30,
                                                    mf=1.0, hc=1.0))
    dt: dict = field(default_factory=lambda: dict(qtz=55.5, cal=47.6, dol=43.5, sh=90.0, fl=189.0))
    # volumetric photoelectric cross-section U = Pe * electron density
    u: dict = field(default_factory=lambda: dict(qtz=4.79, cal=13.77, dol=9.00, sh=9.0, fl=0.40))


def _clamp01(x):
    return x.clamp(EPS, 1.0 - EPS)


# ----------------------------------------------------------------------------- nuclear
def bulk_density(phi, vsh, v_qtz, v_cal, v_dol, sxo, ep: EndPoints | None = None):
    """Bulk density [g/cc], flushed-zone fluid."""
    ep = ep or EndPoints()
    r = ep.rho
    rho_fl = sxo * r["mf"] + (1.0 - sxo) * r["hc"]
    return phi * rho_fl + vsh * r["sh"] + v_qtz * r["qtz"] + v_cal * r["cal"] + v_dol * r["dol"]


def neutron_porosity(phi, vsh, v_qtz, v_cal, v_dol, sxo, ep: EndPoints | None = None):
    """Neutron porosity [v/v, limestone units], linear volumetric approximation."""
    ep = ep or EndPoints()
    n = ep.nphi
    hi_fl = sxo * n["mf"] + (1.0 - sxo) * n["hc"]
    return phi * hi_fl + vsh * n["sh"] + v_qtz * n["qtz"] + v_cal * n["cal"] + v_dol * n["dol"]


def photoelectric(phi, vsh, v_qtz, v_cal, v_dol, rhob, ep: EndPoints | None = None):
    """Photoelectric factor Pe [b/e] from the volumetric cross-section U."""
    ep = ep or EndPoints()
    u = ep.u
    u_b = phi * u["fl"] + vsh * u["sh"] + v_qtz * u["qtz"] + v_cal * u["cal"] + v_dol * u["dol"]
    rho_e = (rhob + 0.1883) / 1.0704
    return u_b / rho_e.clamp_min(0.5)


def gamma_ray(vsh, gr_clean=15.0, gr_shale=120.0):
    """Linear gamma-ray index model [gAPI]; end-points are per-well nuisance parameters."""
    return gr_clean + vsh * (gr_shale - gr_clean)


# ----------------------------------------------------------------------------- sonic
def _matrix_dt(vsh, v_qtz, v_cal, v_dol, ep: EndPoints):
    d = ep.dt
    solid = (vsh + v_qtz + v_cal + v_dol).clamp_min(EPS)
    return (vsh * d["sh"] + v_qtz * d["qtz"] + v_cal * d["cal"] + v_dol * d["dol"]) / solid


def sonic_wyllie(phi, vsh, v_qtz, v_cal, v_dol, ep: EndPoints | None = None):
    """Wyllie time-average compressional slowness [us/ft]."""
    ep = ep or EndPoints()
    return phi * ep.dt["fl"] + (1.0 - phi) * _matrix_dt(vsh, v_qtz, v_cal, v_dol, ep)


def sonic_raymer(phi, vsh, v_qtz, v_cal, v_dol, ep: EndPoints | None = None):
    """Raymer-Hunt-Gardner slowness [us/ft]: V = (1-phi)^2 Vma + phi Vfl (low-porosity branch)."""
    ep = ep or EndPoints()
    v_ma = 1.0 / _matrix_dt(vsh, v_qtz, v_cal, v_dol, ep)
    v = (1.0 - phi) ** 2 * v_ma + phi / ep.dt["fl"]
    return 1.0 / v.clamp_min(EPS)


# ----------------------------------------------------------------------------- resistivity
def log10_rt_archie(phi, sw, m, n, rw, a=1.0):
    """log10 of Archie resistivity: Rt = a Rw / (phi^m Sw^n)."""
    phi, sw = _clamp01(phi), _clamp01(sw)
    arw = a * rw
    log_arw = torch.log10(arw) if torch.is_tensor(arw) else math.log10(arw)
    return log_arw - m * torch.log10(phi) - n * torch.log10(sw)


def conductivity_archie(phi, sw, m, n, rw, a=1.0):
    phi, sw = _clamp01(phi), _clamp01(sw)
    return phi**m * sw**n / (a * rw)


def log10_rt_simandoux(phi, sw, m, n, rw, vsh, rsh=4.0, a=1.0):
    """Simandoux-type shaly model: 1/Rt = phi^m Sw^n / (a Rw) + Vsh Sw / Rsh."""
    c = conductivity_archie(phi, sw, m, n, rw, a) + vsh * _clamp01(sw) / rsh
    return -torch.log10(c.clamp_min(1e-9))


def log10_rt_dual_porosity(phi, sw_macro, f_micro, m, n, rw, m_micro=None, vsh=None, rsh=4.0, a=1.0):
    """Dual-porosity parallel-conduction model for microporous chert.

    Porosity is split into micro-pores (fraction f_micro of phi, always fully water saturated,
    i.e. capillary-bound water) and macro-pores (water saturation sw_macro). The two systems
    conduct in parallel:
        1/Rt = phi_mic^m_mic / (a Rw) + phi_mac^m Sw_mac^n / (a Rw)  [+ Vsh/Rsh]
    With f_micro = 0 this is exactly Archie. The bound water keeps Rt low even when the
    macro-pores hold hydrocarbon, which is the low-resistivity-pay mechanism.
    """
    phi = _clamp01(phi)
    f = f_micro.clamp(0.0, 1.0) if torch.is_tensor(f_micro) else torch.as_tensor(float(f_micro))
    m_micro = m if m_micro is None else m_micro
    phi_mic = (f * phi).clamp_min(EPS)
    phi_mac = ((1.0 - f) * phi).clamp_min(EPS)
    c = phi_mic**m_micro / (a * rw) * (f > 0) + conductivity_archie(phi_mac, sw_macro, m, n, rw, a)
    if vsh is not None:
        c = c + vsh / rsh
    return -torch.log10(c.clamp_min(1e-9))


def total_sw(sw_macro, f_micro):
    """Total water saturation of the dual-porosity system."""
    return f_micro + (1.0 - f_micro) * sw_macro


def bulk_volume_hydrocarbon(phi, sw_macro, f_micro):
    return phi * (1.0 - total_sw(sw_macro, f_micro))


# ----------------------------------------------------------------------------- nuisance
def apply_nuisance(curve, offset=0.0, gain=1.0):
    """Per-well additive/multiplicative nuisance (unknown environmental corrections,
    neutron matrix convention, tool calibration)."""
    return gain * curve + offset


NEUTRON_MATRIX_SHIFT = {"LS": 0.0, "SS": 0.04, "DOL": -0.03}
"""Approximate apparent-porosity shift [v/v] of a neutron curve recorded on a sandstone or
dolomite matrix relative to limestone units (mid-porosity linearisation; prior mean for the
per-well neutron offset when the matrix convention is uncertain)."""
