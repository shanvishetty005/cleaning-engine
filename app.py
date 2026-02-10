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
# Corporate Styling
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

        .card {
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 14px;
            padding: 18px;
            background: rgba(255,255,255,0.02);
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
# Reference Folder Setup
# -----------------------------
REF_DIR = "datasets/reference"
os.makedirs(REF_DIR, exist_ok=True)


def save_if_uploaded(uploaded_file, filename):
    if uploaded_file is not None:
        path = os.path.join(REF_DIR, filename)
        with open(path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return path
    return None


# -----------------------------
# Header
# -----------------------------
st.title("Cleaning Engine")
st.write("Upload a CSV file, apply cleaning rules, and export standardized outputs.")
st.divider()

# -----------------------------
# Session Output Folder
# -----------------------------
session_id = st.session_state.get("session_id")
if not session_id:
    session_id = str(uuid.uuid4())[:8]
    st.session_state["session_id"] = session_id

output_dir = os.path.join("outputs", session_id)

# -----------------------------
# Sidebar Config
# -----------------------------
st.sidebar.header("Configuration")

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

export_powerbi = st.sidebar.checkbox("Generate Power BI Output", value=True)
generate_report = st.sidebar.checkbox("Generate Comparison Report", value=True)

st.sidebar.divider()

with st.sidebar.expander("About Cleaning Engine", expanded=True):
    st.markdown("""
    **Purpose**
    Internal CSV cleaning + standardization engine.

    **Outputs**
    - Cleaned dataset
    - Power BI dataset
    - Comparison report
    """)

# -----------------------------
# Layout
# -----------------------------
left, right = st.columns([1.3, 1])

with left:

    st.subheader("1) Upload Data")
    st.write("<div class='card'>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])
    st.write("</div>", unsafe_allow_html=True)

    # -----------------------------
    # NEW: Reference Files Upload
    # -----------------------------
    st.subheader("Reference Files (Optional)")
    st.write("<div class='card'>", unsafe_allow_html=True)

    company_master_file = st.file_uploader(
        "Company Master File",
        type=["csv"],
        key="company_master"
    )

    company_additions_file = st.file_uploader(
        "Company Master Additions",
        type=["csv"],
        key="company_additions"
    )

    review_file = st.file_uploader(
        "Importer Needs Review List",
        type=["csv"],
        key="review_list"
    )

    st.caption("If not uploaded → default reference files will be used.")
    st.write("</div>", unsafe_allow_html=True)

    st.subheader("2) Run Cleaning")
    st.write("<div class='card'>", unsafe_allow_html=True)
    run_clicked = st.button("Run Cleaning", use_container_width=True)
    st.write("</div>", unsafe_allow_html=True)

with right:
    st.subheader("File Details")
    st.write("<div class='card'>", unsafe_allow_html=True)

    if uploaded_file:
        st.write("File:", uploaded_file.name)
    else:
        st.write("No file uploaded.")

    st.write("</div>", unsafe_allow_html=True)

# -----------------------------
# Run Cleaning
# -----------------------------
if uploaded_file and run_clicked:

    os.makedirs(output_dir, exist_ok=True)

    input_csv_path = os.path.join(output_dir, "raw_uploaded.csv")

    with open(input_csv_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # ✅ Save reference files if provided
    save_if_uploaded(company_master_file, "company_master.csv")
    save_if_uploaded(company_additions_file, "company_master_additions.csv")
    save_if_uploaded(review_file, "importer_needs_review.csv")

    start = time.time()

    with st.spinner("Processing..."):
        cleaned_df, summary, outputs = run_cleaning_job(
            input_csv_path=input_csv_path,
            output_dir=output_dir,
            config=config
        )

    exec_time = round(time.time() - start, 2)

    if not export_powerbi:
        outputs.pop("powerbi_file", None)

    if not generate_report:
        outputs.pop("comparison_report", None)

    # -----------------------------
    # Results
    # -----------------------------
    st.divider()
    st.subheader("Results")

    st.write("<div class='card'>", unsafe_allow_html=True)
    st.json(summary)

    c1, c2, c3 = st.columns(3)
    c1.metric("Rows", cleaned_df.shape[0])
    c2.metric("Columns", cleaned_df.shape[1])
    c3.metric("Time (s)", exec_time)

    st.write("</div>", unsafe_allow_html=True)

    st.write("<div class='card'>", unsafe_allow_html=True)
    st.dataframe(cleaned_df.head(20), use_container_width=True)
    st.write("</div>", unsafe_allow_html=True)

    # -----------------------------
    # Downloads
    # -----------------------------
    st.subheader("Downloads")

    if "cleaned_file" in outputs:
        with open(outputs["cleaned_file"], "rb") as f:
            st.download_button("Download Cleaned File", f, "cleaned_file.csv")

    if "powerbi_file" in outputs:
        with open(outputs["powerbi_file"], "rb") as f:
            st.download_button("Download Power BI File", f, "cleaned_powerbi.csv")

    if "comparison_report" in outputs:
        with open(outputs["comparison_report"], "rb") as f:
            st.download_button("Download Comparison Report", f, "comparison.csv")

    st.success("Cleaning completed successfully.")

# -----------------------------
# Footer
# -----------------------------
st.markdown(
    "<div class='footer'>Internal Tool | Cleaning Engine v1.0</div>",
    unsafe_allow_html=True
)
