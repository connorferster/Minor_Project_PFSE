from pytest import approx, raises
from columns import Column, SteelColumn, Load

C00 = Column(0, 0, 0, 0, 0, 0, 0)  # An empty column
C01 = Column(4800, 120000, 1600e6, 900e6, 1, 1, 19.2)  # mm, MPa
C02 = Column(160, 42.78, 1710.59, 679.91, 2.0, 1.0, 50.0)  # inch, ksi


def test_radius_of_gyration():
    with raises(ZeroDivisionError):
        C00.radius_of_gyration("x")
        C00.radius_of_gyration("y")
    assert C01.radius_of_gyration("x") == approx(115.47005383792515)
    assert C01.radius_of_gyration("y") == approx(86.60254037844386)
    assert C02.radius_of_gyration("x") == approx(6.323427946965752)
    assert C02.radius_of_gyration("y") == approx(3.986624434349398)


def test_euler_buckling_load():
    with raises(ZeroDivisionError):
        C00.radius_of_gyration("x")
    assert C01.euler_buckling_load("x") == approx(13159.472534785811)
    assert C01.euler_buckling_load("y") == approx(7402.203300817018)
    assert C02.euler_buckling_load("x") == approx(16.487154875448674)
    assert C02.euler_buckling_load("y") == approx(13.106333453798175)


SC00 = SteelColumn(
    height=0,
    area=0,
    Ix=0,
    Iy=0,
    kx=0,
    ky=0,
    E=0,
    column_tag="CNull",
    fy=345,
    axial_loads=Load(D=0, L=0, S=0, W=0, E=0),
    phi=0.9,
)
SC01 = SteelColumn(
    height=3250,
    area=16500,
    Ix=308e6,
    Iy=100e6,
    kx=1,
    ky=1,
    E=200e3,
    column_tag="W310x129",
    fy=345,
    axial_loads=Load(D=820000, L=1045100, S=0, W=0, E=0),
    phi=0.9,
)
SC02 = SteelColumn(
    height=160,
    area=42.78,
    Ix=1710.59,
    Iy=679.91,
    kx=2.0,
    ky=1.0,
    E=29007.548,
    column_tag="C02",
    fy=50.038,
    axial_loads=Load(D=9.2, L=10.3, S=0, W=0, E=0),
    phi=0.9,
)
SC03 = SteelColumn(
    height=4000,
    area=47700,
    Ix=1130e6,
    Iy=344e6,
    kx=1.0,
    ky=1.0,
    E=200e3,
    column_tag="W310x375",
    fy=345,
    axial_loads=Load(D=2000e3, L=3000e3, S=0, W=0, E=0),
    phi=0.9,
)


def test_factored_axial_capacity():
    with raises(ZeroDivisionError):
        SC00.factored_axial_capacity(n=1.34)
    # Value of Cr calculated by jabacus.com - similar to steel handbook @ 4470 kN
    assert SC01.factored_axial_capacity(n=1.34) == approx(4465e3, rel=1e-3)
    # Value of Cr calculated by jabacus.com for SI equiv. then manually converted
    assert SC02.factored_axial_capacity(n=1.34) == approx(1698.175, rel=1e-3)
    # Value of Cr provided by CISC steel handbook
    assert SC03.factored_axial_capacity(1.34) == approx(12300e3, rel=1e-3)


def test_factored_dcr():
    assert SC01.factored_dcr(n=1.34) == approx(0.58101620, rel=1e-6)
