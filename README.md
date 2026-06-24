# 🎓 TGECET 2026 College Allotment Finder

[![Live Demo](https://img.shields.io/badge/Live%20Demo-GitHub%20Pages-blueviolet?style=for-the-badge&logo=github)](https://nomaan5541.github.io/tgecet-allotment-finder/)
[![Star on GitHub](https://img.shields.io/badge/Star%20on%20GitHub-🌟-yellow?style=for-the-badge&logo=github)](https://github.com/nomaan5541/tgecet-allotment-finder)
[![Creator Instagram](https://img.shields.io/badge/Instagram-@VIRUS__BOSS-E4405F?style=for-the-badge&logo=instagram)](https://www.instagram.com/VIRUS_BOSS)

A premium, interactive web application designed to search, filter, and analyze the **TGECET 2026 College Allotments**. With data compiled for **8,706 students**, this tool helps you instantly find where your friends got allotted!

---

## ✨ Features

- **🔍 Smart Search:** Search students instantly by **Name** or **Hall Ticket Number**.
- **🏢 College Browser:** View all students allotted to a specific college.
- **⚡ Branch-wise Filtering:** Filter results dynamically by engineering/technology branch.
- **📊 Rank Sorting:** Sort students by rank (ascending/descending) or alphabetically.
- **🎨 Premium UI/UX:** Ultra-modern dark mode interface featuring glassmorphic cards, glowing status indicators, and an interactive WebGL neon-orb background shader.
- **⭐ Friend Finder Star:** Found your friend? Easily star the repository to show support!

---

## 🛠️ Tech Stack & Architecture

### **Frontend & Visuals**
* **Core:** Semantic HTML5, CSS3 (Custom Variables, Modern Flexbox/Grid)
* **Logic:** Vanilla JavaScript (ES6+, dynamic client-side filtering, pagination, and state management)
* **Animations:** Canvas-based interactive WebGL Shader rendering flowing, neon-colored floating orbs responding to pointer movements.

### **Data Engineering & Scraping**
* **Python Scrapers:** Custom automation using **Selenium WebDriver** and direct requests with robust retries/checkpointing (`scrape_allotments.py`, `retry_failed.py`).
* **Data Processing:** Cleaned and compiled using **Pandas** to export:
  - Cleaned JSON data for instant web search (`allotment_data.json`).
  - Excel sheet format for offline analytical use (`TGECET_2026_College_Allotments.xlsx`).

---

## 🚀 Running Locally

### 1. Clone the repository
```bash
git clone https://github.com/nomaan5541/tgecet-allotment-finder.git
cd tgecet-allotment-finder
```

### 2. Start a local server
To avoid CORS issues when fetching the local JSON database file, start a simple HTTP server:

**Using Python:**
```bash
python -m http.server 8080
```

**Using Node.js (Live Server / http-server):**
```bash
npx http-server -p 8080
```

Open `http://localhost:8080` in your web browser.

---

## 🗃️ Data Structure & Update Guide

If you wish to update or scrape allotments again, python script modules are available in the root folder:

1. **`scrape_allotments.py`**: Scrapes the official TGECET portal. Saves checkpoint progress to `scrape_progress.json`.
2. **`retry_failed.py`**: Runs through missing or failed college pages to ensure 100% data completion.
3. **`prepare_data.py`**: Combines progress checkpoints, parses HTML, structures student arrays, and generates `allotment_data.json` and `TGECET_2026_College_Allotments.xlsx`.

---

## 👨‍💻 Creator & Links

Developed with 💜 by **Nomaan**.
* **Instagram:** [@VIRUS_BOSS](https://www.instagram.com/VIRUS_BOSS)
* **GitHub Repository:** [tgecet-allotment-finder](https://github.com/nomaan5541/tgecet-allotment-finder)

*If you found this tool helpful and located your friends, please drop a ⭐ star on the repository!*
