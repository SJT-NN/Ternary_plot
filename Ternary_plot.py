import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import mpltern  # registers ternary projection in matplotlib
import seaborn as sns
import colorcet as cc
from matplotlib.ticker import MultipleLocator, AutoMinorLocator

st.set_page_config(page_title="Excel to Ternary Plot Viewer", layout="wide")

st.title("🔺 Excel to Ternary Plot Viewer")
st.text("The code can be found on https://github.com/SJT-NN?tab=repositories")

# --- Upload Excel file ---
uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])

if uploaded_file:
    # Get sheet names and select sheet
    xls = pd.ExcelFile(uploaded_file)
    sheet_names = xls.sheet_names
    sheet_name = st.selectbox("Select sheet", sheet_names)

    # Load the selected sheet in full
    df = pd.read_excel(uploaded_file, sheet_name=sheet_name)
    
    # Drop unnamed junk columns and strip spaces
    #df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
    #df.columns = df.columns.str.strip()

    st.subheader(f"Preview of Data — Sheet: {sheet_name}")
    st.dataframe(df.head())
    
    average_col = None
    for col in df.columns:
        if df[col].astype(str).str.contains("Average", case=False, na=False).any():
            average_col = col
            break

    # --- Checkbox filter ---
    average_filter = st.checkbox("Only show rows where 'Average' column is not NaN")
    
    # --- Find column containing the string "Average" anywhere in the dataframe ---
    if average_filter and average_col:
        df = df[df[average_col].notna()]
    # --- Column selection for ternary plot ---
    cols = df.columns.tolist()
    col_a = st.selectbox("Column for A-axis (top)", cols)
    col_b = st.selectbox("Column for B-axis (bottom left)", cols)
    col_c = st.selectbox("Column for C-axis (bottom right)", cols)

    # --- Custom axis labels ---
    label_a = st.text_input("Custom label for A-axis (top)", value='Fat (%)')
    label_b = st.text_input("Custom label for B-axis (bottom left)", value='Carbohydrates (%)')
    label_c = st.text_input("Custom label for C-axis (bottom right)", value='Protein (%)')


    # Column selection for category/color grouping
    col_type = st.selectbox("Column for Data Type (color grouping)", ["None"] + cols)

    # --- Display controls ---
    point_size = st.slider("Scatter point size", 10, 200, 50)
    plot_width = st.slider("Plot width", 4, 16, 7)
    plot_height = st.slider("Plot height", 4, 16, 7)

    if col_a and col_b and col_c:
        selected_cols = [col_a, col_b, col_c]
        if col_type != "None":
            selected_cols.append(col_type)

        # --- Clean data: convert to numeric & drop NaNs ---
        tern_df = df[selected_cols].copy()
        df.columns = df.columns.astype(str).str.strip()
        for axis_col in [col_a, col_b, col_c]:
            if isinstance(tern_df[axis_col], pd.DataFrame):
                tern_df[axis_col] = pd.to_numeric(tern_df[axis_col].iloc[:, 0], errors="coerce")
            else:
                tern_df[axis_col] = pd.to_numeric(tern_df[axis_col], errors="coerce")
        tern_df = tern_df.dropna(subset=[col_a, col_b, col_c])

        
        # --- Checkbox for energy conversion ---
        energy_conversion = st.checkbox("Convert from mass (%) to energy (%)")
        
        if energy_conversion:
            # Apply Atwater factors
            tern_df["Fat_energy"] = tern_df[col_a] * 9
            tern_df["Carb_energy"] = tern_df[col_b] * 4
            tern_df["Protein_energy"] = tern_df[col_c] * 4
        if tern_df.empty:
            st.error("No valid numeric rows found after cleaning.")
        else:
            fig = plt.figure(figsize=(plot_width, plot_height))
            ax = fig.add_subplot(projection='ternary',ternary_sum=100.0)

            if col_type != "None":
                categories = tern_df[col_type].astype(str).unique()
                palette_source = st.selectbox(
                    "Choose color palette source",
                    ["Matplotlib tab20", "Seaborn deep", "Seaborn tab10", "Seaborn Set3", "ColorCET glasbey"]
                )

                if palette_source.startswith("Matplotlib"):
                    colors = plt.get_cmap("tab20").colors
                elif palette_source.startswith("Seaborn"):
                    sns_name = palette_source.split(" ")[1]
                    colors = sns.color_palette(sns_name, n_colors=len(categories))
                elif palette_source.startswith("ColorCET"):
                    colors = list(cc.glasbey)

                for idx, cat in enumerate(categories):
                    sub = tern_df[tern_df[col_type].astype(str) == cat]
                    ax.scatter(
                        sub[col_a], sub[col_b], sub[col_c],
                        s=point_size,
                        alpha=0.8,
                        color=colors[idx % len(colors)],
                        label=str(cat)
                    )
                ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1))
            else:
                ax.scatter(
                    tern_df[col_a], tern_df[col_b], tern_df[col_c],
                    s=point_size, alpha=0.7
                )

            
            # Axis labels 
            ax.set_tlabel(label_a) 
            ax.set_llabel(label_b) 
            ax.set_rlabel(label_c) 
            # Axis ticks 
            ax.taxis.set_major_locator(MultipleLocator(100/3)) 
            ax.laxis.set_major_locator(MultipleLocator(100/3)) 
            ax.raxis.set_major_locator(MultipleLocator(100/3)) 
            
            ax.grid(True) 
            st.pyplot(fig)
