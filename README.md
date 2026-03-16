# Healthy Cafe Zone 🍽️ - Smart Healthy Cafeteria Management System

[![Python](https://img.shields.io/badge/Python-3.8+-brightgreen.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.3.3-blue.svg)](https://flask.palletsprojects.com/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0+-4479A1.svg)](https://www.mysql.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![OTP Auth](https://img.shields.io/badge/Auth-OTP%20Secure-orange.svg)](https://github.com/)

> **AI-Powered Healthy Indian Cafeteria** 🚀  
> *Secure OTP Login • Admin Dashboard • PDF Invoices • Real-time Orders*

[🌐 Local Demo](http://127.0.0.1:3000) • [📖 API Docs](#-api-reference) • [🐛 Issues](https://github.com/ayusjakhmola25/Healthy-Cafe/issues)

---

## 📋 Table of Contents
- [✨ Overview](#-overview)
- [🎯 Features](#-features)
- [🛠️ Tech Stack](#️-tech-stack)
- [🚀 Quick Start](#-quick-start)
- [📸 Screenshots](#-screenshots)
- [📖 Usage](#-usage)
- [🔌 API Reference](#-api-reference)
- [📁 Structure](#-project-structure)
- [🚀 Deployment](#-deployment)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)

---

## ✨ Overview

**Healthy Cafe Zone** is a full-stack Flask application for managing a healthy Indian cafeteria. It features secure user authentication (OTP via email), e-commerce (cart/orders/payment with GST/PDF invoices), personalized analytics, and a comprehensive admin panel for business operations.

Focuses on healthy foods (e.g., Oats Idli, Palak Paneer, Ragi Dosa) with diet categorization and meal_mode filtering (breakfast/lunch/dinner).

---

## 🎯 Features

### 👥 **User Features**
- 🔐 **Secure Auth**: Register/Login with OTP (Gmail SMTP), bcrypt passwords, login history/IP tracking
- 🍽️ **Menu Browsing**: Filtered by meal_mode/category, image gallery (30+ healthy items)
- 🛒 **Shopping Cart**: Add/remove items, guest/logged-in persistence
- 💳 **Checkout**: Orders, PDF invoices (ReportLab with GST 18% + delivery), payment simulation
- 📊 **Profile**: Personal details, login stats, order history, nutritional insights (cal/protein/carbs)

### 👨‍💼 **Admin Panel** (`/admin`)
- 📈 **Dashboard**: Users/orders/revenue/low-stock metrics
- 👥 **Users**: List/manage all users
- 🍽️ **Menu**: CRUD menu_items (toggle active, category, price/image)
- 📦 **Inventory**: Stock tracking/alerts
- 📋 **Orders**: View/confirm/cancel user orders
- 🔒 **Security Logs**: Login history audit
- ⚙️ **Settings**: meal_mode (all/breakfast/lunch/dinner) filtering

### 🔧 **Backend Excellence**
- 🛡️ **Security**: Flask-Limiter rate limiting, session mgmt, password validation (8-12 chars, upper/num/special)
- 📄 **PDF Invoices**: Branded with tax calc, auto-generated base64
- 📈 **Analytics**: Real-time login/order stats, guest order tracking
- 🔄 **DB**: MySQL idempotent schema init, efficient queries
- 🤖 **AI Ready**: Recommendation stubs (pandas/scikit-learn deps)

---

## 🛠️ Tech Stack

| Component | Technology | Version |
|-----------|------------|---------|
| **Framework** | Flask | 2.3.3 |
| **Database** | MySQL | 8.0+ |
| **Auth** | bcrypt + OTP (SMTP) | - |
| **PDF** | ReportLab | 4.0.4 |
| **Rate Limit** | Flask-Limiter | 3.5.0 |
| **CORS/Email** | Flask-CORS/Mail | 4.0.0/0.9.1 |
| **Frontend** | Jinja2 + HTML/CSS/JS | - |
| **ML/Analysis** | pandas + scikit-learn | 2.0.3/1.3.0 |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- MySQL 8.0+ (create `healthy_cafe_db`, update creds in `app.py`)
- Git

```bash
# Clone
git clone <your-repo-url> Healthy-Cafe
cd Healthy-Cafe

# Virtualenv
python -m venv venv
# Windows: venv\Scripts\activate
source venv/bin/activate  # Linux/Mac

# Install deps
pip install -r requirements.txt

# Start MySQL & create DB/users (use init_schema() in app.py)
# Edit app.py: host/user/pass/database

# Run
python app.py
```
🌐 Open [http://127.0.0.1:3000](http://127.0.0.1:3000)

**Demo Creds**:
- User: register new or email any@ex.com/pass@123 (OTP to healthycafe2025@gmail.com)
- Admin: Create admin user (role='admin') or check app.py

---

## 📸 Screenshots

| Cafeteria Menu | Cart & Orders | Profile Analytics |
|---------------|---------------|-------------------|
| ![Menu](static/images/cafelogo.jpeg) | ![Cart](static/images/healthy.jpeg) | ![Profile](static/images/indian.jpeg) |

| Admin Dashboard | Admin Menu CRUD | PDF Invoice Sample |
|-----------------|-----------------|-------------------|
| ![Dashboard](static/images/palak_paneer_with_brown_rice_601212bc.jpg) | ![Menu](static/images/ragi_dosa_with_sambar_25da86d7.jpg) | ![Invoice](static/images/chicken_biryani_2988b1c7.jpg) |

*(Replace with actual screenshots; images are healthy food reps)*

---

## 📖 Usage

**User Flow**:
1. Register/Login (OTP email) → Profile setup
2. Browse `/cafeteria` (filtered menu) → Add to cart
3. `/cart` → `/payment` (save order + PDF)
4. `/orders`/`/profile` for history/analytics

**Admin** (`/admin` → login):
- Dashboard metrics, manage users/menu/inventory/orders
- Toggle meal_mode in Settings

---

## 🔌 API Reference

| Endpoint | Method | Description | Auth |
|----------|--------|-------------|------|
| `/register` | POST | Create user | - |
| `/send-login-otp` | POST | Send OTP | - |
| `/verify-login-otp` | POST | Login | - |
| `/food-items` | GET | Active menu | user |
| `/add-to-cart` | POST | Add item | - |
| `/save-order` | POST | Guest order | - |
| `/generate-invoice` | POST | PDF base64 | - |
| `/admin/menu-items` | POST | Admin CRUD | admin |

*Full routes in app.py. Session-based auth.*

---

## 📁 Structure

```
Healthy-Cafe/
├── app.py              # Flask app + all routes/DB
├── requirements.txt    # Deps
├── README.md          # 📄 This file
├── TODO.md            # Tasks
├── static/            # CSS/JS/images (30+ foods)
└── templates/         # Jinja HTML
    ├── user pages...  # cafeteria/cart etc.
    └── admin/         # dashboard/menu etc.
```

---

## 🚀 Deployment

**Heroku/Render**:
```bash
# Procfile: web: python app.py
# Set env: MYSQL_HOST/user/pass/db
git push heroku main
```

**Docker** (future):
```
FROM python:3.11-slim
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 3000
CMD ["python", "app.py"]
```

Update Gmail app password for prod SMTP.

---

## 🤝 Contributing

1. Fork → `git clone + feature/branch`
2. Commit: `git commit -m "feat: add X"`
3. PR to `main`
4. Tests: Add to `tests/` (pytest), `pip install pytest`
5. Docs: Update README/API

Issues: [GitHub Issues](https://github.com/issues)

---

## 📄 License
MIT License - © 2025 Healthy Cafe Zone. See [LICENSE](LICENSE).

---

<div align="center">
⭐ **Star if useful!** · **Made with ❤️ for healthy eating**  
![Metrics](https://img.shields.io/badge/maintenance-active-green.svg)
</div>
