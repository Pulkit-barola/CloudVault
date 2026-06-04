# ☁️ CloudVault

CloudVault is a cloud-based file storage and management platform built using Python, Streamlit, SQLite, and Amazon S3.

It allows users to securely upload, download, search, and delete files while tracking metadata and storage analytics through an interactive dashboard.

---

## 🚀 Live Demo

Add your deployed Streamlit URL here:

(https://cloudvault72.streamlit.app/)

---

## 📂 GitHub Repository

Add your GitHub repository URL here:

[https://github.com/yourusername/CloudVault](https://github.com/Pulkit-barola/CloudVault)

---

## ✨ Features

* Upload files to Amazon S3
* Download files directly from S3
* Delete files from S3
* Search stored files
* Metadata management using SQLite
* Storage usage monitoring
* File type analytics dashboard
* Recent uploads tracking
* Cloud-ready architecture

---

## 🏗️ Architecture

User → Streamlit UI → AWS S3 Storage

```
                     ↓

                SQLite Metadata Database
```

---

## 🛠️ Tech Stack

### Frontend

* Streamlit

### Backend

* Python

### Database

* SQLite

### Cloud Services

* Amazon S3
* AWS IAM

### Libraries

* Pandas
* Boto3
* Python-Dotenv

### Version Control

* Git
* GitHub

---

## ☁️ AWS Services Used

### Amazon S3

Used for storing uploaded files in the cloud.

### AWS IAM

Used to securely manage access permissions through Access Keys and Secret Keys.

---

## 📊 Project Features

### File Upload

Upload files directly to Amazon S3.

### File Download

Download stored files from S3.

### File Deletion

Remove files from both S3 and metadata records.

### Analytics Dashboard

Visualize uploaded file types and storage usage.

### Search System

Quickly locate files using keyword search.

---

## 📦 Installation

Clone the repository:

git clone [https://github.com/yourusername/CloudVault.git](https://github.com/Pulkit-barola/CloudVault)

cd CloudVault

Install dependencies:

pip install -r requirements.txt

---

## 🔐 Environment Variables

Create a `.env` file in the project root:

AWS_ACCESS_KEY_ID=YOUR_ACCESS_KEY

AWS_SECRET_ACCESS_KEY=YOUR_SECRET_KEY

AWS_REGION=ap-south-1

AWS_BUCKET_NAME=cloudvault-storage-pulkit

---

## ▶️ Run Locally

streamlit run app.py

---

## 📸 Screenshots

Add screenshots of:

* Dashboard
* File Upload
* AWS S3 Bucket Objects
* Analytics Dashboard

---

## 🔮 Future Enhancements

* User Authentication
* File Sharing Links
* Role-Based Access Control
* AWS DynamoDB Integration
* AWS Lambda Integration
* Multi-User Support
* File Versioning

---

## 👨‍💻 Author

Pulkit Barola

Cloud Engineering & Software Development Enthusiast
