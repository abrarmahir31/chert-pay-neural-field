"""Joint label-free inversion: spatial parameter field + per-sample rock properties.

Unknowns
  * parameter field g(x, y) -> (m, n, f_micro), a small MLP on Fourier features (bounded outputs);
  * per-sample properties (free variables): phi, vsh, mineral split, macro-pore Sw;
  * per-well nuisance terms: neutron and density offsets, GR end-points, flushing exponent k
    (Sxo = Sw^k), a correction to the header Rmf.
Loss: masked Gaussian misfit of every available curve with FIXED noise scales, plus Gaussian
priors on the nuisance terms. (Noise scales are not learned: with free per-sample variables a
learned variance would collapse to zero.)
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import torch
from torch import nn

from chertfield.physics import forward as fw

BOUNDS = {"m": (1.5, 3.0), "n": (1.2, 2.8), "f_micro": (0.0, 0.9)}


@dataclass
class InversionConfig:
    n_frequencies: int = 4
    hidden: int = 64
    layers: int = 3
    extent_km: tuple = (57.0, 52.0)
    steps: int = 3000
    lr_field: float = 2e-3
    lr_latent: float = 3e-2
    rw: float = 0.045
    sigma: dict = field(default_factory=lambda: dict(RHOB=0.015, NPHI=0.01, GR=4.0, LRT=0.03,
                                                     LRXO=0.05, DT=1.5, PE=0.15))
    use_curves: tuple = ("RHOB", "NPHI", "GR", "LRT", "LRXO", "DT", "PE")
    fixed: dict = field(default_factory=dict)       # e.g. {"n": 2.0, "f_micro": 0.0}
    constant: tuple = ()                            # parameters learned as ONE scalar (no field)
    know_flushing_exponent: float | None = None     # oracle: fix k
    know_rmf_exactly: bool = False                  # oracle: no Rmf correction
    prior_sd: dict = field(default_factory=lambda: dict(nphi_off=0.02, rhob_off=0.02, k=0.08,
                                                        log_rmf=0.15))
    k_prior_mean: float = 0.2
    resistivity: str = "dual_porosity"              # or "archie"
    seed: int = 0


class FourierEncoder(nn.Module):
    def __init__(self, n_frequencies: int):
        super().__init__()
        self.register_buffer("freq", 2.0 ** torch.arange(n_frequencies) * math.pi)
        self.out_dim = 2 + 4 * n_frequencies

    def forward(self, xy01):
        a = xy01[..., None] * self.freq
        return torch.cat([xy01, a.sin().flatten(-2), a.cos().flatten(-2)], dim=-1)


class ParamField(nn.Module):
    """(x, y) in km -> dict of bounded rock-physics parameters."""

    names = ("m", "n", "f_micro")

    def __init__(self, cfg: InversionConfig):
        super().__init__()
        self.cfg = cfg
        self.enc = FourierEncoder(cfg.n_frequencies)
        dims = [self.enc.out_dim] + [cfg.hidden] * cfg.layers
        net = []
        for a, b in zip(dims[:-1], dims[1:], strict=True):
            net += [nn.Linear(a, b), nn.SiLU()]
        self.net = nn.Sequential(*net, nn.Linear(cfg.hidden, len(self.names)))
        nn.init.zeros_(self.net[-1].weight)
        nn.init.zeros_(self.net[-1].bias)
        self.const = nn.Parameter(torch.zeros(len(self.names)))
        self.register_buffer("extent", torch.tensor(cfg.extent_km, dtype=torch.float32))

    def forward(self, xy_km):
        raw = self.net(self.enc(xy_km / self.extent))
        out = {}
        for i, k in enumerate(self.names):
            if k in self.cfg.fixed:
                out[k] = torch.full_like(raw[..., i], float(self.cfg.fixed[k]))
                continue
            r = self.const[i].expand_as(raw[..., i]) if k in self.cfg.constant else raw[..., i]
            lo, hi = BOUNDS[k]
            out[k] = lo + (hi - lo) * torch.sigmoid(r)
        return out


class JointInversion(nn.Module):
    def __init__(self, xy_km, obs: dict, mask: dict, rmf_obs, cfg: InversionConfig):
        super().__init__()
        self.cfg = cfg
        torch.manual_seed(cfg.seed)
        f32 = lambda a: torch.as_tensor(a, dtype=torch.float32)  # noqa: E731
        self.register_buffer("xy", f32(xy_km))
        self.curves = [c for c in cfg.use_curves if c in obs]
        for c in self.curves:
            m = torch.as_tensor(mask[c], dtype=torch.bool) & torch.isfinite(f32(obs[c]))
            self.register_buffer(f"obs_{c}", torch.nan_to_num(f32(obs[c])))
            self.register_buffer(f"mask_{c}", m)
        self.register_buffer("log_rmf_obs", f32(rmf_obs).log())
        W, N = self.obs_RHOB.shape
        self.field = ParamField(cfg)
        # initial porosity from the limestone density-neutron average
        phi0 = (((2.71 - self.obs_RHOB) / 1.66 + self.obs_NPHI) / 2).clamp(0.02, 0.5)
        self.phi_raw = nn.Parameter(torch.logit(phi0 / 0.6))
        self.vsh_raw = nn.Parameter(torch.full((W, N), -2.0))
        self.min_raw = nn.Parameter(torch.zeros(W, N, 3))
        self.sw_raw = nn.Parameter(torch.full((W, N), 1.0))
        self.nphi_off = nn.Parameter(torch.zeros(W, 1))
        self.rhob_off = nn.Parameter(torch.zeros(W, 1))
        self.gr_clean = nn.Parameter(torch.full((W, 1), 20.0))
        self.gr_slope_raw = nn.Parameter(torch.full((W, 1), math.log(250.0)))
        self.k_raw = nn.Parameter(torch.zeros(W, 1))
        self.log_rmf_corr = nn.Parameter(torch.zeros(W, 1))

    # ------------------------------------------------------------------ state
    def properties(self):
        phi = 0.6 * torch.sigmoid(self.phi_raw)
        vsh = 0.5 * torch.sigmoid(self.vsh_raw) * (1 - phi)
        solid = 1 - phi - vsh
        w = torch.softmax(self.min_raw, dim=-1)
        return dict(phi=phi, vsh=vsh, v_qtz=solid * w[..., 0], v_cal=solid * w[..., 1],
                    v_dol=solid * w[..., 2], sw_macro=torch.sigmoid(self.sw_raw))

    def flushing_exponent(self):
        if self.cfg.know_flushing_exponent is not None:
            return torch.full_like(self.k_raw, float(self.cfg.know_flushing_exponent))
        return 0.05 + 0.45 * torch.sigmoid(self.k_raw + math.log((0.2 - 0.05) / (0.5 - 0.2)))

    def params_at_wells(self):
        return self.field(self.xy)

    def predict(self):
        p = self.properties()
        par = {k: v[:, None] for k, v in self.params_at_wells().items()}
        vol = (p["phi"], p["vsh"], p["v_qtz"], p["v_cal"], p["v_dol"])
        k = self.flushing_exponent()
        sxo_mac = p["sw_macro"] ** k
        sxo_tot = fw.total_sw(sxo_mac, par["f_micro"])
        rhob = fw.bulk_density(*vol, sxo_tot)
        rmf = torch.exp(self.log_rmf_obs[:, None]
                        + (0.0 if self.cfg.know_rmf_exactly else self.log_rmf_corr))
        if self.cfg.resistivity == "dual_porosity":
            lrt = fw.log10_rt_dual_porosity(p["phi"], p["sw_macro"], par["f_micro"], par["m"],
                                            par["n"], self.cfg.rw, vsh=p["vsh"])
            lrxo = fw.log10_rt_dual_porosity(p["phi"], sxo_mac, par["f_micro"], par["m"],
                                             par["n"], rmf, vsh=p["vsh"])
        else:
            lrt = fw.log10_rt_archie(p["phi"], p["sw_macro"], par["m"], par["n"], self.cfg.rw)
            lrxo = fw.log10_rt_archie(p["phi"], sxo_mac, par["m"], par["n"], rmf)
        pred = dict(
            RHOB=rhob + self.rhob_off,
            NPHI=fw.neutron_porosity(*vol, sxo_tot) + self.nphi_off,
            GR=self.gr_clean + p["vsh"] * torch.exp(self.gr_slope_raw),
            LRT=lrt, LRXO=lrxo, DT=fw.sonic_raymer(*vol), PE=fw.photoelectric(*vol, rhob),
        )
        return pred, p, par

    def loss(self):
        pred, _, _ = self.predict()
        terms = {}
        for c in self.curves:
            m = getattr(self, f"mask_{c}")
            r = (pred[c] - getattr(self, f"obs_{c}")) / self.cfg.sigma[c]
            terms[c] = 0.5 * (r[m] ** 2).sum()
        sd = self.cfg.prior_sd
        prior = 0.5 * ((self.nphi_off / sd["nphi_off"]) ** 2).sum()
        prior = prior + 0.5 * ((self.rhob_off / sd["rhob_off"]) ** 2).sum()
        prior = prior + 0.5 * ((self.log_rmf_corr / sd["log_rmf"]) ** 2).sum()
        prior = prior + 0.5 * (((self.flushing_exponent() - self.cfg.k_prior_mean) / sd["k"]) ** 2).sum()
        n_obs = sum(int(getattr(self, f"mask_{c}").sum()) for c in self.curves)
        return (sum(terms.values()) + prior) / n_obs, {k: float(v.detach()) for k, v in terms.items()}

    def fit(self, log_every: int = 0):
        cfg = self.cfg
        latent = [p for n, p in self.named_parameters() if not n.startswith("field.")]
        opt = torch.optim.Adam([{"params": self.field.parameters(), "lr": cfg.lr_field},
                                {"params": latent, "lr": cfg.lr_latent}])
        sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, cfg.steps)
        hist = []
        for step in range(cfg.steps):
            opt.zero_grad()
            loss, _ = self.loss()
            loss.backward()
            opt.step()
            sched.step()
            if log_every and (step % log_every == 0 or step == cfg.steps - 1):
                hist.append((step, float(loss)))
        return hist

    @torch.no_grad()
    def chi2_per_curve(self):
        pred, _, _ = self.predict()
        out = {}
        for c in self.curves:
            m = getattr(self, f"mask_{c}")
            r = (pred[c] - getattr(self, f"obs_{c}")) / self.cfg.sigma[c]
            out[c] = float((r[m] ** 2).mean()) if m.any() else float("nan")
        return out
