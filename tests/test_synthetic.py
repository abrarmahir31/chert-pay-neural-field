import numpy as np
import pytest

pytest.importorskip("torch")
from chertfield.synthetic.benchmark import SynthConfig, make_benchmark  # noqa: E402

CFG = dict(n_wells=12, n_samples=40)


def test_deterministic_and_shapes():
    a, b = make_benchmark(SynthConfig(seed=3, **CFG)), make_benchmark(SynthConfig(seed=3, **CFG))
    c = make_benchmark(SynthConfig(seed=4, **CFG))
    assert np.array_equal(a["truth"]["m"], b["truth"]["m"])
    assert not np.array_equal(a["truth"]["m"], c["truth"]["m"])
    assert a["obs"]["RHOB"].shape == (12, 40) and a["xy_km"].shape == (12, 2)


def test_physical_ranges_and_closure():
    d = make_benchmark(SynthConfig(seed=0, **CFG))
    t = d["truth"]
    total = t["phi"] + t["vsh"] + t["v_qtz"] + t["v_cal"] + t["v_dol"]
    assert np.allclose(total, 1.0)
    for k in ("phi", "vsh", "v_qtz", "v_cal", "v_dol", "sw_macro", "sw_total"):
        assert t[k].min() >= 0 and t[k].max() <= 1
    assert 1.5 < t["m"].min() and t["m"].max() < 2.6
    assert 1.9 < np.nanmin(d["clean"]["RHOB"]) and np.nanmax(d["clean"]["RHOB"]) < 2.9
    assert np.all(t["sw_macro"][t["wet_well"]] == 1.0)


def test_masks_whole_wells_and_core_set_complete():
    d = make_benchmark(SynthConfig(seed=1, n_wells=80, n_samples=10))
    for k in ("RHOB", "NPHI", "GR", "LRT"):
        assert d["mask"][k].all()
    frac_dt = d["mask"]["DT"][:, 0].mean()
    assert 0.05 < frac_dt < 0.45  # about 20 % of wells carry sonic, as in the real data
    assert np.isnan(d["obs"]["DT"][~d["mask"]["DT"]]).all()


def test_pay_wells_less_resistive_effect_of_microporosity():
    hi = make_benchmark(SynthConfig(seed=2, fmic_field=(0.6, 0.0, 10.0), **CFG))
    lo = make_benchmark(SynthConfig(seed=2, fmic_field=(0.05, 0.0, 10.0), **CFG))
    pay = hi["truth"]["sw_macro"] < 0.5
    assert np.median(hi["clean"]["LRT"][pay]) < np.median(lo["clean"]["LRT"][pay])
