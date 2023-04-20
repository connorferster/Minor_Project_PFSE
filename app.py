import streamlit as st
import plotly.graph_objects as go
import sample_app_module as sam

st.header("Comparison of factored axial resistance of two doubly-symmetric columns over a height range")

st.sidebar.subheader("Results Parameters")
min_height = st.sidebar.number_input("Minimum column height (mm)", value=200)
max_height = st.sidebar.number_input("Maximum column height (mm)", value=30000)
interval = st.sidebar.number_input("Height step interval (mm)", value=200)

# Column A
st.sidebar.subheader("Column section 'A'")
area_a = st.sidebar.number_input("**Area A** ($mm^2$)", value=1000)
i_x_a = st.sidebar.number_input("Ix A (10e6 $mm^4$)", value=200)
i_y_a = st.sidebar.number_input("Iy A (10e6 $mm^4$)", value=100)
E_a = st.sidebar.number_input("Elastic modulus A (MPa)", value=200e3)
fy_a = st.sidebar.number_input("Yield strength A (MPa)", value=350)

# Column B
st.sidebar.subheader("Column section 'B'")
area_b = st.sidebar.number_input("Area B ($mm^2$)", value=500)
i_x_b = st.sidebar.number_input("Ix B (10e6 $mm^4$)", value=100)
i_y_b = st.sidebar.number_input("Iy B (10e6 $mm^4$)", value=50)
E_b = st.sidebar.number_input("Elastic modulus B (MPa)", value=200e3)
fy_b = st.sidebar.number_input("Yield strength B (MPa)", value=350)

# Calculation of "resistance lines"
results = sam.compare_two_columns(
    min_height,
    max_height,
    interval,
    area_a,
    i_x_a * 1e6,
    i_y_a * 1e6,
    E_a,
    fy_a,
    area_b,
    i_x_b * 1e6,
    i_y_b * 1e6,
    E_b,
    fy_b,
)


height_input = st.number_input(label="Height", min_value=min_height, max_value=max_height)
# Calculation of individual point for plot marker and example calculations
example_latex_a, factored_load_a = sam.calc_pr_at_given_height(
    area_a, 
    i_x_a*1e6, 
    i_y_a*1e6, 
    1.0, 
    1.0, 
    height_input,
    E_a, 
    fy_a, 
    1.34
    )

example_latex_b, factored_load_b = sam.calc_pr_at_given_height(
    area_b, 
    i_x_b*1e6, 
    i_y_b*1e6, 
    1.0, 
    1.0, 
    height_input,
    E_b, 
    fy_b, 
    1.34
    )

fig = go.Figure()

# Plot lines
fig.add_trace(
    go.Scatter(
    x=results["a"][1], 
    y=results["a"][0],
    line={"color": "red"},
    name="Column A"
    )
)
fig.add_trace(
    go.Scatter(
    x=results["b"][1], 
    y=results["b"][0],
    line={"color": "teal"},
    name="Column B"
    )
)

fig.add_trace(
    go.Scatter(
        y=[height_input],
        x=[factored_load_a],
        name="Example Calculation: Column A"
    )
)

fig.add_trace(
    go.Scatter(
        y=[height_input],
        x=[factored_load_b],
        name="Example Calculation: Column B"
    )
)

fig.layout.title.text = "Factored axial resistance of Column A and Column B"
fig.layout.xaxis.title = "Factored axial resistance, N"
fig.layout.yaxis.title = "Height of column, mm"


st.plotly_chart(fig)

calc_expander_a = st.expander(label="Sample Calculation, Column A")
with calc_expander_a:
    for calc in example_latex_a:
        st.latex(
            calc
        )

calc_expander_b = st.expander(label="Sample Calculation, Column B")
with calc_expander_b:
    for calc in example_latex_b:
        st.latex(
            calc
        )