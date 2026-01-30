import os
import uuid
import time
import streamlit as st

from cleaning_engine.service import run_cleaning_job


# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(
    page_title="Cleaning Engine",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------
# Corporate Styling (Blue + Green)
# -----------------------------
st.markdown(
    """
    <style>
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }

        h1, h2, h3 {
            font-family: "Inter", sans-serif;
            letter-spacing: 0.2px;
        }

        div.stButton > button {
            background: linear-gradient(90deg, #0B5ED7 0%, #198754 100%);
            color: white;
            border-radius: 10px;
            padding: 0.6rem 1rem;
            border: none;
            font-weight: 600;
        }
        div.stButton > button:hover {
            filter: brightness(1.05);
        }

        div.stDownloadButton > button {
            border-radius: 10px;
            padding: 0.6rem 1rem;
            font-weight: 600;
        }

        .card {
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 14px;
            padding: 18px;
            background: rgba(255,255,255,0.02);
        }

        .muted {
            color: rgba(255,255,255,0.65);
            font-size: 0.95rem;
        }

        .footer {
            margin-top: 35px;
            padding-top: 10px;
            border-top: 1px solid rgba(255,255,255,0.08);
            color: rgba(255,255,255,0.55);
            font-size: 0.85rem;
            text-align: center;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# Header
# -----------------------------
st.title("Cleaning Engine")
st.write(
    "<div class='muted'>Upload a CSV file, apply cleaning rules, and export standardized outputs.</div>",
    unsafe_allow_html=True
)
st.divider()

# -----------------------------
# Session-specific output folder
# -----------------------------
session_id = st.session_state.get("session_id")
if not session_id:
    session_id = str(uuid.uuid4())[:8]
    st.session_state["session_id"] = session_id

output_dir = os.path.join("outputs", session_id)

# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.header("Configuration")
st.sidebar.write("Select the operations to apply during cleaning:")

if "select_all_ops" not in st.session_state:
    st.session_state["select_all_ops"] = True

c1, c2 = st.sidebar.columns(2)

with c1:
    if st.button("Select All", use_container_width=True):
        st.session_state["select_all_ops"] = True

with c2:
    if st.button("Clear All", use_container_width=True):
        st.session_state["select_all_ops"] = False

select_all = st.session_state["select_all_ops"]

config = {
    "standardize_columns": st.sidebar.checkbox("Standardize Column Names", value=select_all),
    "normalize_nulls": st.sidebar.checkbox("Normalize Null Values", value=select_all),
    "trim_text": st.sidebar.checkbox("Trim Text Fields", value=select_all),
    "standardize_companies": st.sidebar.checkbox("Standardize Company Names", value=select_all),
    "standardize_dates": st.sidebar.checkbox("Standardize Date Columns", value=select_all),
    "convert_numeric": st.sidebar.checkbox("Convert Numeric Columns", value=select_all),
    "remove_empty_rows": st.sidebar.checkbox("Remove Empty Rows", value=select_all),
    "remove_duplicates": st.sidebar.checkbox("Remove Duplicate Records", value=select_all),
    "standardize_no": st.sidebar.checkbox("Standardize 'NO' Column", value=select_all),
}

st.sidebar.divider()

st.sidebar.subheader("Export Options")
export_powerbi = st.sidebar.checkbox("Generate Power BI Output", value=True)
generate_report = st.sidebar.checkbox("Generate Comparison Report", value=True)

st.sidebar.divider()

# -----------------------------
# Sidebar About Section
# -----------------------------
with st.sidebar.expander("About Cleaning Engine", expanded=True):
    st.markdown(
        """
        **Purpose**  
        Cleaning Engine is an internal tool for standardizing and cleaning raw CSV datasets.

        **Outputs Generated**
        - Cleaned dataset (standardized + cleaned)
        - Power BI friendly dataset (optional)
        - Comparison report (optional)

        **How to Use**
        1. Upload a CSV file  
        2. Choose cleaning operations (or use Select All)  
        3. Click Run Cleaning  
        4. Download the generated outputs
        """
    )

st.sidebar.caption("Recommended: Keep default settings for standard workflow.")

# -----------------------------
# Main Layout
# -----------------------------
left, right = st.columns([1.25, 1])

with left:
    st.subheader("1) Upload Data")
    st.write("<div class='card'>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])
    st.write("</div>", unsafe_allow_html=True)

    st.subheader("2) Run Cleaning")
    st.write("<div class='card'>", unsafe_allow_html=True)
    run_clicked = st.button("Run Cleaning", use_container_width=True)
    st.write("</div>", unsafe_allow_html=True)

with right:
    st.subheader("File Details")
    st.write("<div class='card'>", unsafe_allow_html=True)

    if uploaded_file is None:
        st.write("No file uploaded.")
    else:
        st.write("File Name:", uploaded_file.name)

    st.write("</div>", unsafe_allow_html=True)

# -----------------------------
# Run Cleaning Action
# -----------------------------
if uploaded_file is None:
    st.info("Please upload a CSV file to begin.")
else:
    if run_clicked:
        os.makedirs(output_dir, exist_ok=True)

        input_csv_path = os.path.join(output_dir, "raw_uploaded.csv")
        with open(input_csv_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        start_time = time.time()

        with st.spinner("Processing..."):
            cleaned_df, summary, outputs = run_cleaning_job(
                input_csv_path=input_csv_path,
                output_dir=output_dir,
                config=config
            )

        end_time = time.time()
        exec_time = round(end_time - start_time, 2)

        # Respect export toggles
        if not export_powerbi:
            outputs.pop("powerbi_file", None)

        if not generate_report:
            outputs.pop("comparison_report", None)

        # Result Section
        st.divider()
        st.subheader("Results")

        # Summary card
        st.write("<div class='card'>", unsafe_allow_html=True)
        st.markdown("**Cleaning Summary**")
        st.json(summary)

        st.markdown("**Execution Statistics**")
        stats_col1, stats_col2, stats_col3 = st.columns(3)
        stats_col1.metric("Rows", cleaned_df.shape[0])
        stats_col2.metric("Columns", cleaned_df.shape[1])
        stats_col3.metric("Execution Time (s)", exec_time)

        st.write("</div>", unsafe_allow_html=True)

        # Preview card
        st.write("<div class='card'>", unsafe_allow_html=True)
        st.markdown("**Preview (first 20 rows)**")
        st.dataframe(cleaned_df.head(20), use_container_width=True)
        st.write("</div>", unsafe_allow_html=True)

        # Downloads
        st.subheader("Downloads")
        d1, d2, d3 = st.columns(3)

        with d1:
            with open(outputs["cleaned_file"], "rb") as f:
                st.download_button(
                    label="Download Cleaned File",
                    data=f,
                    file_name="cleaned_file.csv",
                    mime="text/csv",
                    use_container_width=True
                )

        if "powerbi_file" in outputs:
            with d2:
                with open(outputs["powerbi_file"], "rb") as f:
                    st.download_button(
                        label="Download Power BI Output",
                        data=f,
                        file_name="cleaned_for_powerbi.csv",
                        mime="text/csv",
                        use_container_width=True
                    )

        if "comparison_report" in outputs:
            with d3:
                with open(outputs["comparison_report"], "rb") as f:
                    st.download_button(
                        label="Download Comparison Report",
                        data=f,
                        file_name="comparison_report.csv",
                        mime="text/csv",
                        use_container_width=True
                    )

        st.success("Completed successfully.")

# -----------------------------
# Footer
# -----------------------------
st.markdown(
    "<div class='footer'>Internal Tool | Cleaning Engine v1.0</div>",
    unsafe_allow_html=True
)
