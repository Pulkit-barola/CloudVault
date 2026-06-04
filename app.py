import streamlit as st
import sqlite3
import os
from datetime import datetime
import pandas as pd

UPLOAD_FOLDER = "uploads"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

st.set_page_config(
    page_title="CloudVault",
    page_icon="☁️",
    layout="wide"
)

# Database Connection
conn = sqlite3.connect("files.db", check_same_thread=False)
cursor = conn.cursor()

# Get Metrics First
cursor.execute("SELECT COUNT(*) FROM files")
total_files = cursor.fetchone()[0]

cursor.execute("SELECT SUM(size) FROM files")
total_size = cursor.fetchone()[0]

if total_size is None:
    total_size = 0

# Sidebar
st.sidebar.title("☁️ CloudVault")

st.sidebar.markdown("""
### Features
- Upload Files
- Download Files
- Delete Files
- Search Files
- Storage Analytics
""")

st.sidebar.success("Cloud Ready Architecture")

MAX_STORAGE_MB = 100

used_storage_mb = round(
    total_size / (1024 * 1024),
    2
)

usage_percent = min(
    int((used_storage_mb / MAX_STORAGE_MB) * 100),
    100
)

st.sidebar.subheader("Storage Usage")
st.sidebar.progress(usage_percent)
st.sidebar.write(
    f"{used_storage_mb} MB / {MAX_STORAGE_MB} MB"
)

# Main Title
st.title("☁️ CloudVault")
st.caption("Secure File Management & Storage Platform")

# Upload Section
uploaded_file = st.file_uploader("Upload File")

if uploaded_file:

    if st.button("Upload"):

        filepath = os.path.join(
            UPLOAD_FOLDER,
            uploaded_file.name
        )

        with open(filepath, "wb") as f:
            f.write(uploaded_file.getbuffer())

        cursor.execute(
            """
            INSERT INTO files
            (filename, file_type, size, upload_date)
            VALUES (?, ?, ?, ?)
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

        st.success("File Uploaded Successfully!")
        st.rerun()

# Metrics
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
        round(total_size / 1024, 2)
    )

# Recent Uploads
st.divider()

st.subheader("📋 Recent Uploads")

cursor.execute("""
SELECT filename, file_type, upload_date
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
    st.info("No recent uploads")

# Analytics
st.divider()

st.subheader("📊 File Type Analytics")

cursor.execute("""
SELECT file_type, COUNT(*)
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
        df.set_index("File Type")
    )

# Search
st.divider()

search = st.text_input(
    "🔍 Search Files"
)

cursor.execute(
    """
    SELECT * FROM files
    """
)

rows = cursor.fetchall()

filtered_rows = []

for row in rows:

    if search.lower() in row[1].lower():
        filtered_rows.append(row)

# File Table
st.subheader("📁 Stored Files")

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

        filepath = os.path.join(
            UPLOAD_FOLDER,
            filename
        )

        if os.path.exists(filepath):

            with open(
                filepath,
                "rb"
            ) as file:

                st.download_button(
                    "⬇️",
                    file,
                    file_name=filename,
                    key=f"d{file_id}"
                )

        if st.button(
            "🗑️",
            key=f"x{file_id}"
        ):

            if os.path.exists(filepath):
                os.remove(filepath)

            cursor.execute(
                """
                DELETE FROM files
                WHERE id = ?
                """,
                (file_id,)
            )

            conn.commit()
            st.rerun()