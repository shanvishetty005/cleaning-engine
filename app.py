import os
import uuid
import time
import pandas as pd
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
# Styling
# -----------------------------
st.markdown("""
<style>
.block-container {padding-top:2rem;padding-bottom:2rem;}
div.stButton > button {
    background: linear-gradient(90deg,#0B5ED7,#198754);
    color:white;border-radius:10px;font-weight:600;
}
.card {
    border:1px solid rgba(255,255,255,0.08);
    border-radius:14px;padding:18px;
    background:rgba(255,255,255,0.02);
}
.footer {
    margin-top:35px;padding-top:10px;
    border-top:1px solid rgba(255,255,255,0.08);
    color:rgba(255,255,255,0.55);
    text-align:center;font-size:.85rem;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Reference Paths
# -----------------------------
REF_DIR = "datasets/reference"
os.makedirs(REF_DIR, exist_ok=True)

MASTER_PATH = os.path.join(REF_DIR, "company_master.csv")
ADD_PATH = os.path.join(REF_DIR, "company_master_additions.csv")
REVIEW_PATH = os.path.join(REF_DIR, "importer_needs_review.csv")


def load_csv_safe(path, cols):
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame(columns=cols)


# -----------------------------
# Header
# -----------------------------
st.title("Cleaning Engine")
st.write("Upload CSV → Clean → Export standardized outputs.")
st.divider()

# -----------------------------
# Session Folder
# -----------------------------
sid = st.session_state.get("sid")
if not sid:
    sid = str(uuid.uuid4())[:8]
    st.session_state["sid"] = sid

output_dir = os.path.join("outputs", sid)

# -----------------------------
# Sidebar Config
# -----------------------------
st.sidebar.header("Configuration")

select_all = st.sidebar.checkbox("Select All Ops", True)

config = {
    "standardize_columns": st.sidebar.checkbox("Standardize Columns", select_all),
    "normalize_nulls": st.sidebar.checkbox("Normalize Nulls", select_all),
    "trim_text": st.sidebar.checkbox("Trim Text", select_all),
    "standardize_companies": st.sidebar.checkbox("Standardize Companies", select_all),
    "standardize_dates": st.sidebar.checkbox("Standardize Dates", select_all),
    "convert_numeric": st.sidebar.checkbox("Numeric Convert", select_all),
    "remove_empty_rows": st.sidebar.checkbox("Remove Empty Rows", select_all),
    "remove_duplicates": st.sidebar.checkbox("Remove Duplicates", select_all),
    "standardize_no": st.sidebar.checkbox("Standardize NO", select_all),
}

export_powerbi = st.sidebar.checkbox("PowerBI Output", True)
generate_report = st.sidebar.checkbox("Comparison Report", True)

# -----------------------------
# ✅ Reference Data Editor
# -----------------------------
st.sidebar.divider()
show_ref = st.sidebar.checkbox("Open Reference Editor")

if show_ref:
    st.subheader("Reference Data Editor")

    t1, t2, t3 = st.tabs([
        "Company Master",
        "Master Additions",
        "Needs Review"
    ])

    with t1:
        df = load_csv_safe(MASTER_PATH, ["core_name","standardized_name"])
        edited = st.data_editor(df, num_rows="dynamic", use_container_width=True)
        if st.button("Save Company Master"):
            edited.to_csv(MASTER_PATH, index=False)
            st.success("Saved.")

    with t2:
        df = load_csv_safe(ADD_PATH, ["core_name","standardized_name"])
        edited = st.data_editor(df, num_rows="dynamic", use_container_width=True)
        if st.button("Save Additions"):
            edited.to_csv(ADD_PATH, index=False)
            st.success("Saved.")

    with t3:
        df = load_csv_safe(REVIEW_PATH, ["importer_core_name"])
        edited = st.data_editor(df, num_rows="dynamic", use_container_width=True)
        if st.button("Save Review List"):
            edited.to_csv(REVIEW_PATH, index=False)
            st.success("Saved.")

    st.divider()

# -----------------------------
# Layout
# -----------------------------
left, right = st.columns([1.3,1])

with left:
    st.subheader("Upload Data")
    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
    run_clicked = st.button("Run Cleaning", use_container_width=True)

with right:
    st.subheader("File Info")
    st.write(uploaded_file.name if uploaded_file else "No file")

# -----------------------------
# Run Cleaning
# -----------------------------
if uploaded_file and run_clicked:

    os.makedirs(output_dir, exist_ok=True)
    input_path = os.path.join(output_dir,"raw.csv")

    with open(input_path,"wb") as f:
        f.write(uploaded_file.getbuffer())

    start = time.time()

    with st.spinner("Cleaning..."):
        cleaned_df, summary, outputs = run_cleaning_job(
            input_csv_path=input_path,
            output_dir=output_dir,
            config=config
        )

    exec_time = round(time.time()-start,2)

    if not export_powerbi:
        outputs.pop("powerbi_file",None)
    if not generate_report:
        outputs.pop("comparison_report",None)

    st.divider()
    st.subheader("Results")

    st.json(summary)

    c1,c2,c3 = st.columns(3)
    c1.metric("Rows", cleaned_df.shape[0])
    c2.metric("Cols", cleaned_df.shape[1])
    c3.metric("Time", exec_time)

    st.dataframe(cleaned_df.head(20), use_container_width=True)

    st.subheader("Downloads")

    for k,label in [
        ("cleaned_file","Cleaned"),
        ("powerbi_file","PowerBI"),
        ("comparison_report","Comparison")
    ]:
        if k in outputs:
            with open(outputs[k],"rb") as f:
                st.download_button(f"Download {label}", f)

    st.success("Done.")

# -----------------------------
# Footer
# -----------------------------
st.markdown(
    "<div class='footer'>Cleaning Engine v1.0</div>",
    unsafe_allow_html=True
)
# -----------------------------
# 📘 Reference Manager (POST-RUN)
# -----------------------------
import pandas as pd

st.divider()
st.subheader("📘 Reference Manager")

REF_DIR = "datasets/reference"
MASTER_PATH = os.path.join(REF_DIR, "company_master.csv")
REVIEW_PATH = os.path.join(REF_DIR, "importer_needs_review.csv")

if os.path.exists(MASTER_PATH):

    with st.expander("Open Reference Editor", expanded=False):

        st.markdown("### Company Master (Editable)")

        master_df = pd.read_csv(MASTER_PATH)
        edited_master = st.data_editor(
            master_df,
            num_rows="dynamic",
            use_container_width=True,
            key="master_editor"
        )

        st.markdown("### Importer Needs Review (Auto Generated)")

        if os.path.exists(REVIEW_PATH):
            review_df = pd.read_csv(REVIEW_PATH)
            st.dataframe(review_df, use_container_width=True)
        else:
            st.info("No review file generated yet.")

        # -----------------------------
        # Save Button
        # -----------------------------
        if st.button("💾 Save Master Changes", use_container_width=True):
            edited_master.to_csv(MASTER_PATH, index=False)
            st.success("Company Master updated successfully ✅")
