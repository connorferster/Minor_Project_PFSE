"""
A module for modelling columns in a variety of materials.
"""

from dataclasses import dataclass
from math import pi, sqrt


@dataclass
class Load:
    """
    A data type to represent any kind of scalar load as defined by the NBCC-19 separated
    out by five components:
    D - Dead
    L - Live
    S - Snow and rain
    W - Wind
    E - Earthquake

    The type of load is not important. e.g the Load can represent a moment, line load,
    point load or area load. All it keeps track of is the magnitude of each component.
    """

    D: float
    L: float
    S: float
    W: float
    E: float


## Examples
LD0 = Load(D=0, L=0, S=0, W=0, E=0)  # Empty Load
LD1 = Load(D=23.3, L=50.9, S=3.4, W=0, E=0)
LD2 = Load(D=4.8, L=0, S=0, W=0, E=12.3)
LD3 = Load(D=32.3, L=0, S=0, W=-10.3, E=0)


@dataclass
class Column:
    """
    A data type to represent a theoretical doubly-symmetric column made of a (mostly)
    homogeneous material, e.g. wood, steel, aluminum, etc.

    Units can be any units but should be internally consistent across the properties
    of the column.
    """

    height: float
    area: float
    Ix: float
    Iy: float
    kx: float
    ky: float
    E: float

    def radius_of_gyration(self, axis: str) -> float:
        """
        Returns the calculated radius of gyration about the given axis.
        'axis', can be one of either "x" or "y"
        """
        if axis.lower() == "x":
            r = radius_of_gyration(self.Ix, self.area)
        elif axis.lower() == "y":
            r = radius_of_gyration(self.Iy, self.area)
        return r

    def euler_buckling_load(self, axis: str) -> float:
        """
        Returns the calculated Euler buckling load about the given axis.
        'axis', can be one of either "x" or "y"
        """
        if axis.lower() == "x":
            P_E = eulerbucklingload(self.E, self.Ix, self.kx, self.height)
        elif axis.lower() == "y":
            P_E = eulerbucklingload(self.E, self.Iy, self.ky, self.height)
        return P_E


## Examples
C00 = Column(0, 0, 0, 0, 0, 0, 0)  # An empty column
C01 = Column(4800, 120000, 1600e6, 900e6, 1, 1, 19.2)  # mm, MPa
C02 = Column(160, 42.78, 1710.59, 679.91, 2.0, 1.0, 50.0)  # inch, ksi


@dataclass
class SteelColumn(Column):
    """
    A data type to represent a physical steel column that has loads applied.
    It is assumed that the steel column section is a doubly-symmetric section.

    Based on the Column data type of a general column, this SteelColumn also
    specifies:

    'column_tag', a unique identifier representing the column on the drawing plan
    'fy', the steel yield stress
    'axial_loads', the axial load applied to the top of the column
    'phi', the steel material reduction factor described in CSA S16:19
    """

    column_tag: str
    fy: float
    axial_loads: Load
    phi: float = 0.9

    def factored_axial_load(self) -> float:
        """
        Returns the factored axial load on the column in accordance with
        NBCC-15. The current implementation only accounts for dead, live,
        and snow loads.
        """
        return max_factored_load(self.axial_loads)

    def factored_axial_capacity(self, n: float) -> float:
        """
        Returns the factored axial capacity of self calculated using CSA S16:19
        in accordance with Cl. 13.3.1 about the governing axis.
        'n', a factor required that describes the fabrication method of the section
            Acceptable values are either:
                1.34 for hot-rolled sections (e.g. HSS, W sections)
                2.24 for built-up plate sections (e.g. WT sections)
        """
        return factored_axial_capacity(
            self.area, self.Ix, self.Iy, self.kx, self.ky, self.height, self.E, self.fy, n
        )

    def factored_dcr(self, n: float) -> float:
        """
        Returns the factored demand / capacity ratio for self.
        """
        return self.factored_axial_load() / self.factored_axial_capacity(n)


## Examples
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


### Functions


def max_factored_load(load: Load) -> float:
    """
    Returns a float representing the maximum factored load for the
    loads in 'load' with load combinations as per NBCC-15.
    Current implementation only calculates factored loads for load
    combinations that include dead, live, and snow (no uplift)
    """
    factored_loads = [
        1.4 * load.D,
        1.25 * load.D + 1.5 * load.L,
        1.25 * load.D + 1.5 * load.L + 1.0 * load.S,
        1.25 * load.D + 1.5 * load.S + 1.0 * load.L,
    ]
    return max(factored_loads)


def dl_str_to_load(dl_str: list[str]) -> Load:
    """
    Returns a Load representing the data in 'dl_str'. For the purpose
    of this function, 'dl_str' represents a list of two elements, dead
    and live load, respectively. The returned Load will only have its
    D and L fields populated.
    """
    dead, live = float(dl_str[0]), float(dl_str[1])
    return Load(dead, live, 0, 0, 0)


def radius_of_gyration(I: float, A: float) -> float:
    """
    Calculates teh radius of gyration
    """
    r = sqrt(I / A)
    return r


def eulerbucklingload(E: float, I: float, k: float, L: float):
    """
    Calculates the Euler buckling load of a column
    """
    P_E = (pi**2 * E * I) / (k * L**2)
    return P_E


def factored_axial_capacity(area: float,I_x: float,I_y: float,k_x: float,k_y: float,L: float, E: float,f_y: float,n: float, phi=0.9) -> float:
    """
    Returns the factored axial capacity of self calculated using CSA S16:19
    in accordance with Cl. 13.3.1 about the governing axis.
    'n', a factor required that describes the fabrication method of the section
        Acceptable values are either:
            1.34 for hot-rolled sections (e.g. HSS, W sections)
            2.24 for built-up plate sections (e.g. WT sections)
    """
    P_E_x = eulerbucklingload(E, I_x, k_x, L)
    F_e_x = P_E_x/ area
    P_E_y = eulerbucklingload(E, I_y, k_y, L)
    F_e_y = P_E_y / area
    F_e = min(F_e_x, F_e_y)
    lamb = sqrt(f_y / F_e)
    P_r = phi * area * f_y * ((1 + lamb ** (2 * n)) ** (-1 / n))
    return P_r
