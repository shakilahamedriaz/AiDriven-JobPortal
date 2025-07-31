# 🚀 AIpply – The AI-Powered Job Portal

![Project Banner](https://user-images.githubusercontent.com/73512833/212261623-3b41399a-e8f0-4c31-897b-9524e782803b.png)
<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/python-3.9+-blue.svg">
  <img alt="Django" src="https://img.shields.io/badge/django-4.x-green.svg">
  <img alt="License" src="https://img.shields.io/badge/License-MIT-yellow.svg">
  <img alt="Status" src="https://img.shields.io/badge/status-active-brightgreen">
</p>

<p align="center">
  Welcome to <b>AIpply</b> – the next-generation job portal that seamlessly integrates AI-driven interview preparation with a robust job search engine. Empower your career journey, smarter and more efficiently!
</p>

---

## 📋 Table of Contents

- [About The Project](#-about-the-project)
- [🌟 Core Features](#-core-features)
- [🖼️ Screenshots](#-screenshots)
- [🛠️ Tech Stack](#-tech-stack)
- [🚦 Getting Started](#-getting-started)
- [📝 How It Works](#-how-it-works)
- [🗄️ Database Models](#-database-models)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)
- [🙌 Acknowledgements](#-acknowledgements)

---

## 🎯 About The Project

**AIpply** is a full-featured web application built with Django, designed to bridge the gap between job applicants and employers. It solves two key problems: the anxiety of interview preparation and the difficulty of finding the right candidate or job.

Applicants can not only search for jobs using advanced filters but also practice for interviews with an AI-powered coach that provides real-time feedback. Employers can easily post job openings and manage applications from a dedicated dashboard.

---

## 🌟 Core Features

- **👥 Dual User Roles**: Separate registration, dashboards, and functionalities for **Applicants** and **Employers**.
- **🤖 AI Interviewer**: Practice interviews with an AI that asks relevant questions and provides instant feedback and hints.
- **🗣️ Voice Interaction**: Integrated Web Speech API for read-aloud questions, voice-to-text answers, and immersive practice sessions.
- **🔍 Advanced Job Search**: A powerful search engine to filter jobs by **title**, **company name**, and **location**.
- **💼 Job Management (for Employers)**:
  - Post new job openings with detailed descriptions.
  - View and manage all posted jobs.
  - See a list of applicants for each specific job.
- **📄 Application Tracking (for Applicants)**:
  - Browse and apply to jobs by uploading a **resume** and writing a **cover letter**.
  - View a history of all submitted applications.
- **🔐 Secure Authentication**: Robust user registration, login, and session management.
- **📱 Modern & Responsive UI**: A clean, interactive, and visually appealing interface built with Tailwind CSS and Alpine.js, ensuring a great experience on any device.

---

## 🖼️ Screenshots

| Home Page | AI Interview Session | Job Listings |
| :---: | :---: | :---: |
| ![image1](image1) | ![image2](image2) | ![image4](image4) |
| **Applicant Dashboard** | **Employer Dashboard** | **Interview History** |
| ![image5](image5) | *(Add Employer Dashboard Screenshot)* | ![image6](image6) |

---

## 🛠️ Tech Stack

- **Backend**: Django, Django REST Framework
- **Frontend**: Tailwind CSS, Alpine.js, HTML5
- **AI Integration**: OpenAI GPT API (or your chosen provider)
- **Voice Features**: Web Speech API (Text-to-Speech & Speech Recognition)
- **Database**: PostgreSQL (Production), SQLite3 (Development)
- **Deployment**: Docker, Gunicorn, Nginx (Configuration included)

---

## 🚦 Getting Started

Follow these instructions to get a local copy up and running for development and testing purposes.

### Prerequisites

- Python 3.9+
- Pip & a Virtual Environment tool (`venv`)
- Git

### Installation

1.  **Clone the repository**
    ```bash
    git clone [https://github.com/yourusername/aipply.git](https://github.com/yourusername/aipply.git)
    cd aipply
    ```

2.  **Create and activate a virtual environment**
    ```bash
    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate

    # For Windows
    python -m venv venv
    venv\Scripts\activate
    ```

3.  **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up environment variables**
    - Create a `.env` file in the root project directory.
    - Add your configuration details. See `.env.example` for required variables.
    ```ini
    SECRET_KEY='your-secret-key'
    DEBUG=True
    DATABASE_URL='sqlite:///db.sqlite3' # Or your PostgreSQL URL
    OPENAI_API_KEY='your-openai-api-key'
    ```

5.  **Apply database migrations**
    ```bash
    python manage.py migrate
    ```

6.  **Create a superuser (for admin access)**
    ```bash
    python manage.py createsuperuser
    ```

7.  **Run the development server**
    ```bash
    python manage.py runserver
    ```
    Your project will be available at `http://127.0.0.1:8000/`.

---

## 📝 How It Works

### For Applicants 🧑‍💻
1.  **Register** as an 'Applicant'.
2.  **Search & Filter** for jobs on the main job listings page.
3.  Click on a job to **view details**.
4.  Use the **"AI Interview"** feature to practice for the role.
5.  **Apply** by filling out the form and uploading your resume and cover letter.
6.  Track your application status in your **Dashboard**.

### For Employers 🏢
1.  **Register** as an 'Employer'.
2.  From your dashboard, **Post a New Job**.
3.  **Manage** all your active job listings.
4.  **View Applicants** for each job, including their resumes and cover letters.

---

## 🗄️ Database Models

<details>
<summary>Click to view the core Django Models</summary>

### `Job` Model
Stores all the information related to a job posting.

| Field | Type | Description |
| :--- | :--- | :--- |
| `title` | CharField | The title of the job (e.g., "Software Engineer"). |
| `company_name` | CharField | The name of the company hiring. |
| `location` | CharField | The physical location for the job. |
| `description` | TextField | A detailed description of the role and responsibilities. |
| `posted_by` | ForeignKey | A link to the `Employer` (User) who posted the job. |
| `created_at` | DateTimeField | Timestamp when the job was posted. |

### `Application` Model
Stores a record of each application submitted by a user.

| Field | Type | Description |
| :--- | :--- | :--- |
| `job` | ForeignKey | A link to the `Job` being applied for. |
| `applicant` | ForeignKey | A link to the `Applicant` (User) who applied. |
| `resume` | FileField | The uploaded resume file. |
| `cover_letter`| TextField | The text of the applicant's cover letter. |
| `applied_at` | DateTimeField | Timestamp when the application was submitted. |

</details>

---

## 🤝 Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

For major changes, please open an issue first to discuss what you would like to change.

---

## 📄 License

This project is distributed under the MIT License. See `LICENSE` for more information.

---

## 🙌 Acknowledgements

A special thank you to the creators and maintainers of these amazing tools.

- [Django](https://www.djangoproject.com/)
- [Tailwind CSS](https://tailwindcss.com/)
- [OpenAI](https://openai.com/)
- [Alpine.js](https://alpinejs.dev/)

---

> **AIpply** – Empower your career with AI!
