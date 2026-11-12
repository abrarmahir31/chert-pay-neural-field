"""Smoke tests of the inversion on tiny synthetic data (few optimisation steps)."""
import numpy as np
import pytest

torch = pytest.importorskip("torch")
from chertfield.data.standin import load_standin  # noqa: E402
from chertfield.model.inversion import InversionConfig, JointInversion  # noqa: E402


def make(d, **kw):
    cfg = InversionConfig(steps=30, fixed={"n": 1.8, "f_micro": 0.0}, resistivity="archie",
                          learn_rw=True, device="auto", **kw)
    return JointInversion(d["xy_km"], d["obs"], d["mask"], d["rmf_obs"], cfg,
                          log_rmf_prior_sd=d["log_rmf_prior_sd"])


@pytest.fixture(scope="module")
def data():
    return load_standin(n_wells=10, n_samples=20, seed=0)


def test_loss_decreases_and_outputs_bounded(data):
    m = make(data)
    l0 = float(m.loss()[0])
    m.fit()
    assert float(m.loss()[0]) < l0
    pay = m.pay_indicator()
    assert pay.shape == (10, 20) and np.isfinite(pay).all() and pay.min() >= 0 and pay.max() <= 0.6
    par = m.params_at_wells()
    assert torch.all(par["n"] == 1.8) and torch.all(par["f_micro"] == 0.0)
    assert 1.5 <= float(par["m"].min()) and float(par["m"].max()) <= 3.0


@pytest.mark.parametrize("spatial", ["field", "per_well", "constant"])
def test_spatial_modes(data, spatial):
    m = make(data, spatial=spatial)
    m.fit()
    mm = m.params_at_wells()["m"]
    assert mm.shape == (10,)
    if spatial == "constant":
        assert float(mm.std()) < 1e-6


def test_freeze_shared_keeps_field_and_rw(data):
    a = make(data)
    a.fit()
    b = make(data)
    b.freeze_shared(a)
    before = [p.detach().clone() for p in b.field.net.parameters()]
    b.fit()
    for p, q in zip(b.field.net.parameters(), before, strict=True):
        assert torch.equal(p, q)
    assert float(b.log_rw_delta) == float(a.log_rw_delta)


def test_missing_samples_are_ignored(data):
    d = {**data, "obs": {k: v.copy() for k, v in data["obs"].items()},
         "mask": {k: v.copy() for k, v in data["mask"].items()}}
    d["obs"]["RHOB"][0, :5] = np.nan
    d["mask"]["RHOB"][0, :5] = False
    m = make(d)
    m.fit()
    assert np.isfinite(float(m.loss()[0]))
