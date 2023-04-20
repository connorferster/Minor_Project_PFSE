from structural_columns import columns
from handcalcs.decorator import handcalc

CalcSteelColumn = columns.SteelColumn
calc_renderer = handcalc()

CalcSteelColumn.radius_of_gyration = calc_renderer(columns.SteelColumn.radius_of_gyration)


def compare_two_columns(
    min_height: int, 
    max_height: int,
    interval: int,
    area_a: int,
    i_x_a: int,
    i_y_a: int,
    E_a: int,
    fy_a: int,
    area_b: int,
    i_x_b: int,
    i_y_b: int,
    E_b: int,
    fy_b: int,
) -> dict[str, tuple[list[float], list[float]]]:
    """
    Returns a dictionary with keys "a" and "b". The values for each "a" and "b" represents
    a tuple of x-coordinates and y_coordinates, respectively, used for generating the plots
    of the factored axial resistance of the two columns, "a" and "b".
    
    'min_height': The minimum column height to test
    'max_height': the maximum column height to test
    'interval': the step size at which to generate plot points at
    'area_a': area of column section "a"
    'i_x_a': Moment of inertia about x-axis for columns section "a"
    'i_y_a': Moment of interia about y-axis for columns section "a"
    'E_a': Elastic module for columns section "a"
    'fy_a': Yield strength for columns section "a"
    'area_b': area of column section "b"
    'i_x_b': Moment of inertia about x-axis for columns section "b"
    'i_y_b': Moment of interia about y-axis for columns section "b"
    'E_b': Elastic module for columns section "b"
    'fy_b': Yield strength for columns section "b"
    """
    x_values_a, y_values_a = column_pr_over_height_range(
        min_height,
        max_height,
        interval,
        "Column A",
        area_a,
        i_x_a,
        i_y_a,
        E_a,
        fy_a
    )
    x_values_b, y_values_b = column_pr_over_height_range(
        min_height,
        max_height,
        interval,
        "Column B",
        area_b,
        i_x_b,
        i_y_b,
        E_b,
        fy_b
    )     
    return {
        "a": (x_values_a, y_values_a),
        "b": (x_values_b, y_values_b),
    }

def column_pr_over_height_range(
        min_height: int, 
        max_height: int,
        interval: int,
        column_tag: str,
        area: float, 
        i_x: float, 
        i_y: float,
        E=200e3,
        fy=350,

) -> tuple[list[float], list[float], str]:
    """
    Returns a tuple containing a list of x-coordinates and a list of y-coordinates (respectively).
    The x-coordinates represent height values ranging from 'min_height' to 'max_height' stepping by
    the 'interval'.
    The y-coordinates represent the factored axial resistance (Pr) of the column at each corresponding
    height.
    The factored axial resistance is calculated according to CSA S16-15

    Assumptions:
        * The column is pinned-pinned at the ends with an effective length of k * height
        where k == 1 in both x and y directions.
        * The steel section being calculated is a doubly-symmetric hot-rolled section
    """
    x_values = list(range(min_height, max_height, interval))
    test_column = CalcSteelColumn(
        height=min_height,
        area=area,
        Ix=i_x,
        Iy=i_y,
        kx=1,
        ky=1,
        E=E,
        column_tag=column_tag,
        fy=fy,
        axial_loads=columns.Load(0, 0, 0, 0, 0),
    )
    y_values = []
    for x_value in x_values:
        test_column.height = x_value
        pr = test_column.factored_axial_capacity(1.34)
        y_values.append(pr)

    return x_values, y_values


# Example calcs with handcalcs
hc_renderer = handcalc(override='long')

calc_euler_buckling = hc_renderer(columns.eulerbucklingload)
calc_factored_resistance = hc_renderer(columns.factored_axial_capacity)

def calc_pr_at_given_height(area: float, Ix: float, Iy: float, kx: float, ky: float, L: float, E: float, fy: float, n: float, phi=0.9):
    """
    Doc strings
    """
    xbuckling_latex, _ = calc_euler_buckling(E, Ix, kx, L)
    ybuckling_latex, _ = calc_euler_buckling(E, Iy, ky, L)
    factored_latex, factored_load = calc_factored_resistance(
        area,
        Ix,
        Iy,
        kx,
        ky,
        L,
        E,
        fy,
        n,
        phi
        )
    return [xbuckling_latex, ybuckling_latex, factored_latex], factored_load
