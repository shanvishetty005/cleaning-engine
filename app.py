import os
import uuid
import time
import pandas as pd
import streamlit as st

from cleaning_engine.service import run_cleaning_job


# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="Cleaning Engine",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =====================================================
# STYLE — PROFESSIONAL + HIKAL THEME BUTTON
# =====================================================

st.markdown("""
<style>

.block-container {
    padding-top:1.5rem;
    padding-bottom:2rem;
}

/* ---------- Cards ---------- */

.section-card {
    border:1px solid rgba(255,255,255,0.08);
    border-radius:14px;
    padding:18px;
    background:rgba(255,255,255,0.02);
}

/* ---------- HIKAL THEME BUTTON ---------- */

div.stButton > button {
    background: linear-gradient(90deg, #0B5FA5, #1AA7A1);
    color: white;
    border-radius: 12px;
    border: none;
    font-weight: 600;
    font-size: 1rem;
    padding: 0.6rem 1rem;
    transition: all 0.25s ease-in-out;
}

/* Hover effect */
div.stButton > button:hover {
    background: linear-gradient(90deg, #0A4E8A, #178F89);
    box-shadow: 0 0 0 2px rgba(26,167,161,0.35);
    transform: translateY(-1px);
}

/* Click effect */
div.stButton > button:active {
    transform: translateY(0px) scale(0.98);
}

/* ---------- Download Buttons ---------- */

div.stDownloadButton > button {
    border-radius: 10px;
    font-weight: 600;
}

/* ---------- Footer ---------- */

.footer {
    margin-top:40px;
    padding-top:10px;
    border-top:1px solid rgba(255,255,255,0.08);
    color:rgba(255,255,255,0.55);
    text-align:center;
    font-size:.85rem;
}

</style>
""", unsafe_allow_html=True)



# =====================================================
# PATHS
# =====================================================

REF_DIR = "datasets/reference"
os.makedirs(REF_DIR, exist_ok=True)

MASTER_PATH = os.path.join(REF_DIR, "company_master.csv")
ADD_PATH = os.path.join(REF_DIR, "company_master_additions.csv")
REVIEW_PATH = os.path.join(REF_DIR, "importer_needs_review.csv")

if not os.path.exists(MASTER_PATH):
    pd.DataFrame(columns=["core_name","standardized_name"]).to_csv(MASTER_PATH,index=False)


def load_csv_safe(path, cols):
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame(columns=cols)


# -----------------------------
# Header with Logo (Right Side)
# -----------------------------
logo_path = "cleaning_engine/assets/hikal_logo.png"   # adjust if your path differs

col_title, col_logo = st.columns([5, 1])

with col_title:
    st.markdown("""
        <div style="padding-top:20px">
            <h1 style="margin-bottom:0;">Cleaning Engine</h1>
            <div style="opacity:0.7;font-size:1.1rem;">
                Enterprise Data Cleaning & Standardization Platform
            </div>
        </div>
    """, unsafe_allow_html=True)

with col_logo:
    st.write("")  # spacer
    st.write("")  # spacer pushes logo downward
    if os.path.exists(logo_path):
        st.image(logo_path, width=130)

st.divider()


# =====================================================
# SESSION OUTPUT FOLDER
# =====================================================

sid = st.session_state.get("sid")
if not sid:
    sid = str(uuid.uuid4())[:8]
    st.session_state["sid"] = sid

output_dir = os.path.join("outputs", sid)


# =====================================================
# SIDEBAR — OPERATIONS
# =====================================================

st.sidebar.header("⚙️ Cleaning Operations")

select_all = st.sidebar.checkbox("Select All", True)

config = {
    "standardize_columns": st.sidebar.checkbox("Standardize Columns", select_all),
    "normalize_nulls": st.sidebar.checkbox("Normalize Nulls", select_all),
    "trim_text": st.sidebar.checkbox("Trim Text", select_all),
    "standardize_companies": st.sidebar.checkbox("Standardize Companies", select_all),
    "standardize_dates": st.sidebar.checkbox("Standardize Dates", select_all),
    "convert_numeric": st.sidebar.checkbox("Convert Numeric", select_all),
    "remove_empty_rows": st.sidebar.checkbox("Remove Empty Rows", select_all),
    "remove_duplicates": st.sidebar.checkbox("Remove Duplicates", select_all),
    "standardize_no": st.sidebar.checkbox("Standardize NO", select_all),
}

st.sidebar.divider()

st.sidebar.subheader("📤 Exports")
export_powerbi = st.sidebar.checkbox("PowerBI Output", True)
generate_report = st.sidebar.checkbox("Comparison Report", True)


# =====================================================
# SIDEBAR — REFERENCE MANAGER
# =====================================================

st.sidebar.divider()
st.sidebar.header(" Reference Manager")

if st.sidebar.checkbox("Open Manager"):

    master_df = load_csv_safe(MASTER_PATH, ["core_name","standardized_name"])
    add_df = load_csv_safe(ADD_PATH, ["core_name","standardized_name"])
    review_df = load_csv_safe(REVIEW_PATH, ["unmapped_core_name"])

    # ---------- MASTER ----------
    st.sidebar.subheader("Company Master")

    edited_master = st.sidebar.data_editor(
        master_df,
        num_rows="dynamic",
        use_container_width=True,
        key="master_editor"
    )

    if st.sidebar.button("Save Master"):
        edited_master.drop_duplicates("core_name").to_csv(MASTER_PATH,index=False)
        st.sidebar.success("Saved")


    # ---------- ADDITIONS ----------
    if not add_df.empty:
        st.sidebar.subheader("Suggested Additions")

        add_df = add_df[~add_df["core_name"].isin(master_df["core_name"])]
        add_df["add"] = False

        add_sel = st.sidebar.data_editor(add_df, key="add_editor")

        if st.sidebar.button("Add → Master"):
            rows = add_sel[add_sel["add"]][["core_name","standardized_name"]]
            if not rows.empty:
                new = pd.concat([master_df, rows]).drop_duplicates("core_name")
                new.to_csv(MASTER_PATH,index=False)
                st.sidebar.success(f"Added {len(rows)}")


    # ---------- REVIEW ----------
    if not review_df.empty:
        st.sidebar.subheader("Needs Review")

        review_df["standardized_name"] = ""
        review_df["add"] = False

        rev_sel = st.sidebar.data_editor(review_df, key="review_editor")

        if st.sidebar.button("Review → Master"):
            rows = rev_sel[rev_sel["add"]]
            if not rows.empty:
                rows = rows.rename(columns={"unmapped_core_name":"core_name"})
                rows = rows[["core_name","standardized_name"]]
                new = pd.concat([master_df, rows]).drop_duplicates("core_name")
                new.to_csv(MASTER_PATH,index=False)
                st.sidebar.success(f"Added {len(rows)}")


# =====================================================
# MAIN — UPLOAD
# =====================================================

st.subheader("1️⃣ Upload Data")

uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

run_clicked = st.button("Run Cleaning", use_container_width=True)


# =====================================================
# RUN CLEANING
# =====================================================

if uploaded_file and run_clicked:

    os.makedirs(output_dir, exist_ok=True)

    input_path = os.path.join(output_dir,"raw.csv")

    with open(input_path,"wb") as f:
        f.write(uploaded_file.getbuffer())

    start = time.time()

    with st.spinner("Running cleaning pipeline..."):
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

    # ---------- RESULTS ----------
    st.divider()
    st.subheader("2️⃣ Results")

    c1,c2,c3 = st.columns(3)
    c1.metric("Rows", cleaned_df.shape[0])
    c2.metric("Columns", cleaned_df.shape[1])
    c3.metric("Time (s)", exec_time)

    st.json(summary)

    st.dataframe(cleaned_df.head(25), use_container_width=True)

    # ---------- DOWNLOADS ----------
    st.subheader("3️⃣ Downloads")

    for key,label,name in [
        ("cleaned_file","Cleaned File","cleaned_file.csv"),
        ("powerbi_file","PowerBI File","cleaned_powerbi.csv"),
        ("comparison_report","Comparison Report","comparison.csv")
    ]:
        if key in outputs and os.path.exists(outputs[key]):
            with open(outputs[key],"rb") as f:
                st.download_button(
                    f"Download {label}",
                    f.read(),
                    file_name=name,
                    mime="text/csv",
                    use_container_width=True
                )

    st.success("Cleaning completed successfully ")


# =====================================================
# FOOTER
# =====================================================

st.markdown(
    "<div class='footer'>Cleaning Engine • Internal Data Standardization Tool</div>",
    unsafe_allow_html=True
)
