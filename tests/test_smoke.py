from amo.hw.dds_sim import SimDDS
def test_simdds_smoke():
    d = SimDDS()
    d.set_frequency(0, 1e6)
    d.set_phase(0, 45)
    d.set_amplitude(0, 0.5)
    d.apply_update()
    s = d.read_state()
    assert "ch" in s and s["ch"][0]["f_Hz"] == 1e6
