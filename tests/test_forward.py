"""Forward-model unit tests (analytic limits, monotonicity, gradients, degeneracy)."""
import pytest

torch = pytest.importorskip("torch")
from chertfield.physics import forward as fw  # noqa: E402

T = lambda *a: [torch.tensor(x, dtype=torch.float64) for x in a]  # noqa: E731


def test_density_limits():
    phi, vsh, q, c, d, sxo = T(0.0, 0.0, 0.0, 1.0, 0.0, 1.0)
    assert fw.bulk_density(phi, vsh, q, c, d, sxo).item() == pytest.approx(2.71)
    phi, vsh, q, c, d, sxo = T(0.2, 0.0, 0.8, 0.0, 0.0, 1.0)
    assert fw.bulk_density(phi, vsh, q, c, d, sxo).item() == pytest.approx(0.2 * 1.05 + 0.8 * 2.65)


def test_neutron_limestone_reads_porosity():
    phi, vsh, q, c, d, sxo = T(0.15, 0.0, 0.0, 0.85, 0.0, 1.0)
    assert fw.neutron_porosity(phi, vsh, q, c, d, sxo).item() == pytest.approx(0.15)
    # chert (quartz) matrix reads lower than limestone at the same porosity
    phi, vsh, q, c, d, sxo = T(0.15, 0.0, 0.85, 0.0, 0.0, 1.0)
    assert fw.neutron_porosity(phi, vsh, q, c, d, sxo).item() < 0.15


def test_pe_mineral_ordering():
    def pe(q, c, d):
        a = T(0.0, 0.0, q, c, d)
        rhob = fw.bulk_density(*a, torch.tensor(1.0, dtype=torch.float64))
        return fw.photoelectric(*a, rhob).item()
    assert pe(1, 0, 0) == pytest.approx(1.81, abs=0.1)   # quartz
    assert pe(0, 1, 0) == pytest.approx(5.08, abs=0.15)  # calcite
    assert pe(1, 0, 0) < pe(0, 0, 1) < pe(0, 1, 0)


def test_sonic_limits_and_ordering():
    a = T(0.0, 0.0, 0.0, 1.0, 0.0)
    assert fw.sonic_wyllie(*a).item() == pytest.approx(47.6)
    assert fw.sonic_raymer(*a).item() == pytest.approx(47.6)
    b = T(0.2, 0.0, 0.0, 0.8, 0.0)
    assert fw.sonic_wyllie(*b).item() == pytest.approx(0.2 * 189 + 0.8 * 47.6)
    assert 47.6 < fw.sonic_raymer(*b).item() < 189


def test_archie_value_and_special_cases():
    phi, sw, m, n = T(0.2, 1.0, 2.0, 2.0)
    assert 10 ** fw.log10_rt_archie(phi, sw, m, n, 0.05).item() == pytest.approx(0.05 / 0.04, rel=1e-4)
    sw = torch.tensor(0.5, dtype=torch.float64)
    arch = fw.log10_rt_archie(phi, sw, m, n, 0.05).item()
    zero = torch.tensor(0.0, dtype=torch.float64)
    assert fw.log10_rt_simandoux(phi, sw, m, n, 0.05, zero).item() == pytest.approx(arch, abs=1e-9)
    assert fw.log10_rt_dual_porosity(phi, sw, zero, m, n, 0.05).item() == pytest.approx(arch, abs=1e-5)


def test_dual_porosity_suppresses_resistivity_in_pay():
    phi, sw, m, n = T(0.3, 0.2, 2.0, 2.0)
    f = torch.tensor(0.5, dtype=torch.float64)
    r_arch = fw.log10_rt_archie(phi, sw, m, n, 0.05)
    r_dual = fw.log10_rt_dual_porosity(phi, sw, f, m, n, 0.05)
    assert r_dual < r_arch                       # bound water lowers Rt
    assert fw.total_sw(sw, f).item() == pytest.approx(0.6)
    assert fw.bulk_volume_hydrocarbon(phi, sw, f).item() == pytest.approx(0.3 * 0.4)


def test_gradients_finite():
    x = torch.tensor([0.25, 0.4, 0.3, 2.1, 1.9], dtype=torch.float64, requires_grad=True)
    y = fw.log10_rt_dual_porosity(x[0], x[1], x[2], x[3], x[4], 0.05)
    (g,) = torch.autograd.grad(y, x)
    assert torch.isfinite(g).all() and (g.abs() > 0).all()
    assert g[1] < 0  # more water -> lower resistivity


def test_archie_single_sample_degeneracy_documented():
    """m and Sw trade off exactly at one depth: resistivity alone cannot separate them."""
    phi = torch.tensor(0.2, dtype=torch.float64)
    a = fw.log10_rt_archie(phi, torch.tensor(0.5), torch.tensor(2.0), torch.tensor(2.0), 0.05)
    # raise m by 0.3 and compensate with a higher Sw
    sw2 = 0.5 * 0.2 ** (-0.3 / 2.0)
    b = fw.log10_rt_archie(phi, torch.tensor(sw2), torch.tensor(2.3), torch.tensor(2.0), 0.05)
    assert a.item() == pytest.approx(b.item(), abs=1e-6)
