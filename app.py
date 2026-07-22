import streamlit as st
import sqlite3
import os
from datetime import datetime
import pandas as pd
from dotenv import load_dotenv
import boto3

# ----------------------------
# AWS CONFIG
# ----------------------------

load_dotenv()

AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")

# Streamlit Secrets fallback for cloud deployment
try:
    if not AWS_ACCESS_KEY and "AWS_ACCESS_KEY_ID" in st.secrets:
        AWS_ACCESS_KEY = st.secrets["AWS_ACCESS_KEY_ID"]
    if not AWS_SECRET_KEY and "AWS_SECRET_ACCESS_KEY" in st.secrets:
        AWS_SECRET_KEY = st.secrets["AWS_SECRET_ACCESS_KEY"]
    if not AWS_REGION and "AWS_REGION" in st.secrets:
        AWS_REGION = st.secrets["AWS_REGION"]
    if not BUCKET_NAME and "AWS_BUCKET_NAME" in st.secrets:
        BUCKET_NAME = st.secrets["AWS_BUCKET_NAME"]
except Exception:
    pass

# Case-insensitive loading fallback
if not all([AWS_ACCESS_KEY, AWS_SECRET_KEY, AWS_REGION, BUCKET_NAME]):
    try:
        for k in st.secrets:
            v = st.secrets[k]
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

s3 = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=AWS_REGION
)

# ----------------------------
# PAGE CONFIG
# ----------------------------

st.set_page_config(
    page_title="CloudVault",
    page_icon="☁️",
    layout="wide"
)

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

st.sidebar.markdown("""
### Features
- Upload Files
- Download Files
- Delete Files
- Search Files
- Storage Analytics
- AWS S3 Storage
""")

st.sidebar.success(
    "AWS Cloud Ready Architecture"
)

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

# ----------------------------
# FILE UPLOAD
# ----------------------------

uploaded_file = st.file_uploader(
    "Upload File"
)

if uploaded_file:

    if st.button("Upload"):

        try:

            s3.upload_fileobj(
                uploaded_file,
                BUCKET_NAME,
                uploaded_file.name
            )

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

            st.success(
                "File Uploaded To AWS S3 Successfully!"
            )

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

    st.metric(
        "Total Files",
        total_files
    )

with col2:

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

for row in filtered_rows:

    file_id = row[0]
    filename = row[1]
    file_type = row[2]
    size = row[3]
    upload_date = row[4]

    col1, col2, col3, col4, col5 = st.columns(
        [4, 2, 2, 2, 1]
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

        try:
            download_url = s3.generate_presigned_url(
                'get_object',
                Params={'Bucket': BUCKET_NAME, 'Key': filename},
                ExpiresIn=3600
            )
            st.link_button("⬇️", download_url)
        except:
            st.warning("Not Found")

        if st.button(
            "🗑️",
            key=f"x{file_id}"
        ):

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

            st.rerun()

conn.close()