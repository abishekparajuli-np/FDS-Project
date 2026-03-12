# FDS-Project

## Foundation of Data Science Project

**2nd Year, 3rd Semester**

A data science project featuring a **Cross-Reference Engine** and **Fake News Detector** model developed as part of the Foundation of Data Science course curriculum.

---

## 📋 Table of Contents

- [About the Project](#about-the-project)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
- [Team Members](#team-members)
- [License](#license)

---

## 📖 About the Project

This project is developed as part of the **Foundation of Data Science** course for the 2nd Year, 3rd Semester. It combines two powerful components:

### 🔍 Cross-Reference Engine
The Cross-Reference Engine is the core component of this project. It allows users to verify information by cross-referencing data from multiple sources. The engine analyzes and compares content across various databases and trusted sources to validate the authenticity and accuracy of information.

**Key Capabilities:**
- Multi-source data comparison and validation
- Source credibility scoring
- Real-time cross-referencing of claims and statements
- Aggregated trust score generation

### 🕵️ Fake News Detector
A machine learning model trained to identify and classify fake news articles. The detector works in conjunction with the Cross-Reference Engine to provide comprehensive news verification.

**Key Capabilities:**
- Text classification using ML/NLP techniques
- Probability scoring for fake vs. real news
- Integration with the Cross-Reference Engine for enhanced accuracy

---

## ✨ Features

- **Cross-Reference Verification** - Validate information against multiple trusted sources
- **Fake News Detection** - ML-powered classification of news articles
- **Credibility Scoring** - Generate trust scores based on source reliability
- **User-Friendly Interface** - Simple frontend for easy interaction
- **RESTful API** - Backend API for processing and analysis

---

## 🛠️ Tech Stack

- **Frontend:** JavaScript
- **Backend:** Node.js / Python
- **Machine Learning:** Python, Scikit-learn, NLP libraries
- **Data Processing:** Pandas, NumPy

---

## 📁 Project Structure

```
FDS-Project/
├── app/
│   ├── backend/        # API and cross-reference engine logic
│   └── frontend/       # User interface
├── model/              # Fake news detector ML model
├── README.md
└── ...
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Node.js (v14 or higher)
- Required Python libraries (see requirements.txt)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/abishekparajuli-np/FDS-Project.git
   cd FDS-Project
   ```

2. **Install dependencies**
   ```bash
   # Install Python dependencies for ML model
   pip install -r requirements.txt

   # Install app dependencies
   cd app/backend && npm install
   cd ../frontend && npm install
   ```

3. **Run the application**
   ```bash
   # Start the application
   npm start
   ```

---

## 📊 Usage

1. Enter a news article or claim in the input field
2. The system will:
   - Run the **Fake News Detector** model to classify the content
   - Use the **Cross-Reference Engine** to verify against trusted sources
3. View the combined credibility score and detailed analysis

---

## 👥 Team Members

| Name | GitHub Profile | Role |
|------|----------------|------|
| Kushal Mishra| [@mishrakushalofficial](https://github.com/mishrakushalofficial) | Machine Learning Development|
| Abishek Parajuli | [@abishekparajuli-np](https://github.com/abishekparajuli-np) | Full-Stack Development |
| Komal Kushwaha| [@Komalkush19](https://github.com/Komalkush19) | Machine Learning & Documentation|


---

## 📝 License

This project is for educational purposes as part of the Foundation of Data Science course.

---

<p align="center">
  Made with ❤️ for FDS Course | 2nd Year, 3rd Semester
</p>