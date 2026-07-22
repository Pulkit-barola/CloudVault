import streamlit as st
import sqlite3
import os
from datetime import datetime
import pandas as pd
from dotenv import load_dotenv
import boto3

# ----------------------------
# AWS CONFIG & MODE SELECTION
# ----------------------------

load_dotenv()

# 1. Start with os.environ (case-sensitive)
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")

# 2. Try os.environ case-insensitively if not found
for k, v in os.environ.items():
    k_upper = k.upper()
    if not AWS_ACCESS_KEY and k_upper == "AWS_ACCESS_KEY_ID":
        AWS_ACCESS_KEY = v
    elif not AWS_SECRET_KEY and k_upper == "AWS_SECRET_ACCESS_KEY":
        AWS_SECRET_KEY = v
    elif not AWS_REGION and k_upper == "AWS_REGION":
        AWS_REGION = v
    elif not BUCKET_NAME and k_upper == "AWS_BUCKET_NAME":
        BUCKET_NAME = v

# 3. Try Streamlit Secrets case-insensitively
try:
    for k in st.secrets:
        v = st.secrets[k]
        if isinstance(v, dict):
            # Handle nested dicts if any
            for nk, nv in v.items():
                nk_upper = nk.upper()
                if not AWS_ACCESS_KEY and nk_upper == "AWS_ACCESS_KEY_ID":
                    AWS_ACCESS_KEY = nv
                elif not AWS_SECRET_KEY and nk_upper == "AWS_SECRET_ACCESS_KEY":
                    AWS_SECRET_KEY = nv
                elif not AWS_REGION and nk_upper == "AWS_REGION":
                    AWS_REGION = nv
                elif not BUCKET_NAME and nk_upper == "AWS_BUCKET_NAME":
                    BUCKET_NAME = nv
        else:
            k_upper = k.upper()
            if not AWS_ACCESS_KEY and k_upper == "AWS_ACCESS_KEY_ID":
                AWS_ACCESS_KEY = v
            elif not AWS_SECRET_KEY and k_upper == "AWS_SECRET_ACCESS_KEY":
                AWS_SECRET_KEY = v
            elif not AWS_REGION and k_upper == "AWS_REGION":
                AWS_REGION = v
            elif not BUCKET_NAME and k_upper == "AWS_BUCKET_NAME":
                BUCKET_NAME = v
except Exception:
    pass

# Validate AWS environment variables
is_aws_configured = all([AWS_ACCESS_KEY, AWS_SECRET_KEY, AWS_REGION, BUCKET_NAME])
s3 = None
aws_error = None

# Always try to initialize boto3 client
try:
    s3 = boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        region_name=AWS_REGION
    )
except Exception as e:
    aws_error = str(e)

# ----------------------------
# PAGE CONFIG
# ----------------------------

st.set_page_config(
    page_title="CloudVault",
    page_icon="☁️",
    layout="wide"
)

# Custom Styling
st.markdown("""
<style>
    .metric-container {
        border-radius: 8px;
        padding: 10px;
        background-color: rgba(255,255,255,0.05);
    }
</style>
""", unsafe_allow_html=True)

# ----------------------------
# DATABASE
# ----------------------------

conn = sqlite3.connect(
    "files.db",
    check_same_thread=False
)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT,
    file_type TEXT,
    size INTEGER,
    upload_date TEXT
)
""")

conn.commit()

# ----------------------------
# METRICS
# ----------------------------

cursor.execute(
    "SELECT COUNT(*) FROM files"
)

total_files = cursor.fetchone()[0]

cursor.execute(
    "SELECT SUM(size) FROM files"
)

total_size = cursor.fetchone()[0]

if total_size is None:
    total_size = 0

# ----------------------------
# SIDEBAR
# ----------------------------

st.sidebar.title("☁️ CloudVault")

if is_aws_configured:
    st.sidebar.success("⚡ Mode: AWS S3 Cloud")
else:
    st.sidebar.warning("⚠️ S3 Config Check")

st.sidebar.markdown("""
### Features
- Upload Files
- Download Files
- Delete Files
- Search Files
- Storage Analytics
- AWS S3 Storage
""")

MAX_STORAGE_MB = 100

used_storage_mb = round(
    total_size / (1024 * 1024),
    2
)

usage_percent = min(
    int(
        (used_storage_mb / MAX_STORAGE_MB)
        * 100
    ),
    100
)

st.sidebar.subheader(
    "Storage Usage"
)

st.sidebar.progress(
    usage_percent
)

st.sidebar.write(
    f"{used_storage_mb} MB / {MAX_STORAGE_MB} MB"
)

# ----------------------------
# TITLE
# ----------------------------

st.title("☁️ CloudVault")

st.caption(
    "AWS S3 Powered File Storage System"
)

# Configuration Status Banner
if is_aws_configured:
    st.info(f"Connected to AWS S3 Bucket: `{BUCKET_NAME}`")
else:
    st.warning("⚠️ **AWS S3 Configuration Check:** Some variables might not be configured. If you face upload errors, please verify your credentials.")
    with st.expander("Details & Setup Instructions"):
        st.markdown(f"""
        Please verify your AWS S3 environment variables:
        * `AWS_ACCESS_KEY_ID`: {"Set" if AWS_ACCESS_KEY else "Not Set"}
        * `AWS_SECRET_ACCESS_KEY`: {"Set" if AWS_SECRET_KEY else "Not Set"}
        * `AWS_REGION`: {"Set" if AWS_REGION else "Not Set"}
        * `AWS_BUCKET_NAME`: {"Set" if BUCKET_NAME else "Not Set"}
        
        Create a `.env` file in the project root or configure Secrets on Streamlit Cloud.
        """)
        if aws_error:
            st.error(f"AWS S3 Error: {aws_error}")

# ----------------------------
# FILE UPLOAD
# ----------------------------

uploaded_file = st.file_uploader(
    "Upload File"
)

if uploaded_file:

    if st.button("Upload", use_container_width=True):

        if not BUCKET_NAME:
            st.error("Upload Failed: AWS_BUCKET_NAME is not configured/set.")
        elif not s3:
            st.error("Upload Failed: AWS S3 client could not be initialized. Please check your credentials.")
        else:
            try:
                s3.upload_fileobj(
                    uploaded_file,
                    BUCKET_NAME,
                    uploaded_file.name
                )
                success_msg = "File Uploaded To AWS S3 Successfully!"

                cursor.execute(
                    """
                    INSERT INTO files
                    (filename,file_type,size,upload_date)
                    VALUES (?,?,?,?)
                    """,
                    (
                        uploaded_file.name,
                        uploaded_file.type,
                        uploaded_file.size,
                        datetime.now().strftime(
                            "%Y-%m-%d %H:%M:%S"
                        )
                    )
                )

                conn.commit()

                st.success(success_msg)

                conn.close()
                st.rerun()

            except Exception as e:

                st.error(
                    f"Upload Failed: {e}"
                )

# ----------------------------
# METRICS
# ----------------------------

st.divider()

col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.metric(
            "Total Files",
            total_files
        )

with col2:
    with st.container(border=True):
        st.metric(
            "Storage Used (KB)",
            round(
                total_size / 1024,
                2
            )
        )

# ----------------------------
# RECENT FILES
# ----------------------------

st.divider()

st.subheader(
    "📋 Recent Uploads"
)

cursor.execute("""
SELECT filename,
       file_type,
       upload_date
FROM files
ORDER BY id DESC
LIMIT 5
""")

recent_files = cursor.fetchall()

if recent_files:

    for file in recent_files:

        st.write(
            f"📄 {file[0]} | {file[1]} | {file[2]}"
        )

else:

    st.info(
        "No recent uploads"
    )

# ----------------------------
# ANALYTICS
# ----------------------------

st.divider()

st.subheader(
    "📊 File Type Analytics"
)

cursor.execute("""
SELECT file_type,
       COUNT(*)
FROM files
GROUP BY file_type
""")

analytics = cursor.fetchall()

if analytics:

    df = pd.DataFrame(
        analytics,
        columns=[
            "File Type",
            "Count"
        ]
    )

    st.bar_chart(
        df.set_index(
            "File Type"
        )
    )

# ----------------------------
# SEARCH
# ----------------------------

st.divider()

search = st.text_input(
    "🔍 Search Files"
)

cursor.execute(
    "SELECT * FROM files"
)

rows = cursor.fetchall()

filtered_rows = []

for row in rows:

    if search.lower() in row[1].lower():

        filtered_rows.append(
            row
        )

# ----------------------------
# FILE TABLE
# ----------------------------

st.subheader(
    "📁 Stored Files"
)

if filtered_rows:
    col_h1, col_h2, col_h3, col_h4, col_h5, col_h6 = st.columns([3, 2, 1.5, 2.5, 1, 1])
    with col_h1: st.markdown("**Filename**")
    with col_h2: st.markdown("**Type**")
    with col_h3: st.markdown("**Size**")
    with col_h4: st.markdown("**Upload Date**")
    with col_h5: st.markdown("**Download**")
    with col_h6: st.markdown("**Delete**")

    for row in filtered_rows:

        file_id = row[0]
        filename = row[1]
        file_type = row[2]
        size = row[3]
        upload_date = row[4]

        col1, col2, col3, col4, col5, col6 = st.columns(
            [3, 2, 1.5, 2.5, 1, 1]
        )

        with col1:
            st.write(filename)

        with col2:
            st.write(file_type)

        with col3:
            st.write(
                f"{round(size / 1024, 2)} KB"
            )

        with col4:
            st.write(upload_date)

        with col5:

            if s3 and BUCKET_NAME:
                try:
                    download_url = s3.generate_presigned_url(
                        'get_object',
                        Params={'Bucket': BUCKET_NAME, 'Key': filename},
                        ExpiresIn=3600
                    )
                    st.link_button("⬇️", download_url)
                except:
                    st.warning("Error")
            else:
                st.warning("Unavailable")

        with col6:
            if st.button(
                "🗑️",
                key=f"x{file_id}"
            ):
                if s3 and BUCKET_NAME:
                    try:
                        s3.delete_object(
                            Bucket=BUCKET_NAME,
                            Key=filename
                        )
                    except:
                        pass

                cursor.execute(
                    """
                    DELETE FROM files
                    WHERE id=?
                    """,
                    (file_id,)
                )

                conn.commit()
                conn.close()

                st.rerun()
else:
    st.info("No files stored yet.")

conn.close()