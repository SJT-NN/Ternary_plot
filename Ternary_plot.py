import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import mpltern  # registers ternary projection in matplotlib

st.set_page_config(page_title="Excel to Ternary Plot Viewer", layout="wide")

st.title("🔺 Excel to Ternary Plot Viewer")

# --- Upload Excel file ---
uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])

if uploaded_file:
    # Get sheet names and select sheet
    xls = pd.ExcelFile(uploaded_file)
    sheet_names = xls.sheet_names
    sheet_name = st.selectbox("Select sheet", sheet_names)

    # Load the selected sheet in full
    df = pd.read_excel(uploaded_file, sheet_name=sheet_name)

    st.subheader(f"Preview of Data — Sheet: {sheet_name}")
    st.dataframe(df.head())

    # --- Column selection for ternary plot ---
    cols = df.columns.tolist()
    col_a = st.selectbox("Column for A-axis (top)", cols)
    col_b = st.selectbox("Column for B-axis (bottom left)", cols)
    col_c = st.selectbox("Column for C-axis (bottom right)", cols)

    # Column selection for category/color grouping
    col_type = st.selectbox("Column for Data Type (color grouping)", ["None"] + cols)

    # --- Display controls ---
    point_size = st.slider("Scatter point size", 10, 200, 50)
    plot_width = st.slider("Plot width (inches)", 4, 16, 7)
    plot_height = st.slider("Plot height (inches)", 4, 16, 7)

    if col_a and col_b and col_c:
        # Build selected column list for previewing, cleaning, plotting
        selected_cols = [col_a, col_b, col_c]
        if col_type != "None":
            selected_cols.append(col_type)

        # --- Clean data: convert axis columns to numeric & drop NaNs ---
        tern_df = df[selected_cols].copy()

        for axis_col in [col_a, col_b, col_c]:
            tern_df[axis_col] = pd.to_numeric(tern_df[axis_col], errors="coerce")

        tern_df = tern_df.dropna(subset=[col_a, col_b, col_c])

        if tern_df.empty:
            st.error("No valid numeric rows found after cleaning.")
        else:
            # Optional normalization to sum = 1
            if st.checkbox("Normalize columns so A+B+C = 1"):
                total = tern_df[col_a] + tern_df[col_b] + tern_df[col_c]
                tern_df[col_a] /= total
                tern_df[col_b] /= total
                tern_df[col_c] /= total

            a_vals = tern_df[col_a].values
            b_vals = tern_df[col_b].values
            c_vals = tern_df[col_c].values

            # --- Plot ternary chart ---
            fig = plt.figure(figsize=(plot_width, plot_height))
            ax = fig.add_subplot(projection='ternary')

            if col_type != "None":
                categories = tern_df[col_type].astype(str).unique()
                cmap = plt.get_cmap("tab10")
                for idx, cat in enumerate(categories):
                    sub = tern_df[tern_df[col_type].astype(str) == cat]
                    ax.scatter(
                        sub[col_a], sub[col_b], sub[col_c],
                        s=point_size,
                        alpha=0.8,
                        color=cmap(idx % 10),
                        label=str(cat)
                    )
                ax.legend(title=col_type, loc="upper right", bbox_to_anchor=(1.3, 1))
            else:
                ax.scatter(a_vals, b_vals, c_vals, s=point_size, alpha=0.7)

            # Axis labels and grid
            ax.set_tlabel(col_a)
            ax.set_llabel(col_b)
            ax.set_rlabel(col_c)
            ax.grid(True)

            st.pyplot(fig)
