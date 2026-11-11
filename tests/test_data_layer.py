"""Unit tests on tiny synthetic data (no real logs needed)."""
import numpy as np
import pytest

from chertfield.data import las_io, mnemonics

LAS = """~Version Information
 VERS.   2.0 : CWLS LOG ASCII STANDARD - VERSION 2.0
 WRAP.   NO  : One line per depth step
~Well Information
 STRT.{u}  {a} : START
 STOP.{u}  {b} : STOP
 STEP.{u}  {s} : STEP
 NULL.   -999.25 : NULL
 WELL.   SYNTH 1 : WELL
 API .   15-007-00000 : API
~Parameter Information
 EKB .FT 1500 : KB
 MATR.   0.0000 : NEUTRON MATRIX (0=LIME,1=SAND,2=DOLO)
~Curve Information
 DEPT.{u} : Depth
 GR  .GAPI : Gamma
 RHOB.G/CC : Density
 CNPOR.PU : CN Selected Porosity
 RILD.OHM-M : Deep
~A
"""


def write_las(tmp_path, unit="FT", n=40, top=4500.0, step=0.5):
    rng = np.random.default_rng(0)
    d = top + step * np.arange(n)
    rows = np.c_[d, 40 + rng.random(n), 2.5 + 0.01 * rng.random(n), 15 + rng.random(n),
                 5 + rng.random(n)]
    rows[3, 1] = -999.25
    p = tmp_path / "1.las"
    body = "\n".join(" ".join(f"{x:.4f}" for x in r) for r in rows)
    p.write_text(LAS.format(u=unit, a=d[0], b=d[-1], s=step) + body + "\n")
    return p, d


def test_summarise_las_feet(tmp_path):
    p, d = write_las(tmp_path)
    rec, curves = las_io.summarise_las(p)
    assert rec["parse_ok"] and rec["n_samples"] == 40
    assert rec["depth_top_ft"] == pytest.approx(d[0]) and rec["step_ft"] == pytest.approx(0.5)
    gr = next(c for c in curves if c["mnemonic"] == "GR")
    assert gr["n_valid"] == 39  # the null sample was removed


def test_depth_metres_converted(tmp_path):
    p, d = write_las(tmp_path, unit="M", top=1400.0, step=0.1524)
    rec, _ = las_io.summarise_las(p)
    assert rec["depth_flag"] == "converted_m_to_ft"
    assert rec["depth_top_ft"] == pytest.approx(1400.0 * las_io.FT_PER_M)


def test_bad_file_does_not_raise(tmp_path):
    p = tmp_path / "bad.las"
    p.write_text("this is not a LAS file")
    rec, curves = las_io.summarise_las(p)
    assert rec["parse_ok"] is False or curves == []


@pytest.mark.parametrize(
    "mnem,canon",
    [("RILD", "RDEEP"), ("rll3", "RSHAL"), ("CNLS", "NPHI_LS"), ("CNPOR", "NPHI_UNK"),
     ("DPOR", "DPHI_LS"), ("RHOB:1", "RHOB"), ("GR_1", "GR"), ("DT", "DT"), ("LTEN", None)],
)
def test_classify(mnem, canon):
    assert mnemonics.classify(mnem)[0] == canon


def test_alias_unique_across_canonicals():
    seen = {}
    for canon, spec in mnemonics.load_table()["canonical"].items():
        for a in spec["aliases"]:
            assert seen.setdefault(a.upper(), canon) == canon, f"{a} mapped twice"


def test_porosity_units():
    v = np.array([5.0, 12.0, 20.0, 30.0])
    out, how = mnemonics.to_fraction(v, "PU")
    assert how == "percent" and out.max() == pytest.approx(0.30)
    out, how = mnemonics.to_fraction(v / 100, "PU")  # mislabelled unit
    assert "says_percent" in how and out.max() == pytest.approx(0.30)
    out, how = mnemonics.to_fraction(v / 100, "")
    assert how == "guessed_fraction"


def test_harmonise_masks_and_converts():
    v, _ = mnemonics.harmonise("RHOB", np.array([2500.0, 2650.0]), "KG/M3")
    assert v == pytest.approx([2.5, 2.65])
    v, _ = mnemonics.harmonise("RDEEP", np.array([-1.0, 10.0, 1e6]), "OHMM")
    assert np.isnan(v[0]) and v[1] == 10.0 and np.isnan(v[2])


def test_neutron_matrix_text():
    f = mnemonics.neutron_matrix_from_text
    assert f("CN Limestone Porosity") == "LS"
    assert f("", "1.0000 NEUTRON MATRIX (0=LIME,1=SAND,2=DOLO)") == "SS"
    assert f("CN Selected Porosity") is None
