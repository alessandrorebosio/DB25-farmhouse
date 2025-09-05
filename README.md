# 🏡 Farmhouse - Agritourism Management System

## 📋 Project Description
This project implements a comprehensive database system for managing an agritourism facility. The system handles:
- 🛏️ Guest reservations (rooms, restaurant tables, pool loungers)
- 🚜 Activity bookings (farm visits, sports facilities)
- 📦 Package deals creation and management
- ⭐ Reviews and feedback system
- 👥 Staff administration tools
- 📊 Real-time availability tracking

## 🛠️ Technical Specifications
- **Backend Framework**: Django 5.2.4 (Python)
- **Database**: MySQL
- **Python Version**: 3.10+

## 📁 Project Structure
```
DB25-farmhouse/
├── app/
│   ├── manage.py          # Django management script
│   ├── config/            # Django project configuration
│   │   ├── settings.py    # Main settings
│   │   ├── urls.py        # URL routing
│   │   └── wsgi.py        # WSGI configuration
│   └── core/              # Main application
│       ├── models.py      # Database models
│       ├── views.py       # Business logic
│       ├── admin.py       # Admin interface
│       └── migrations/    # Database migrations
├── requirements.txt       # Python dependencies
└── README.md              # This file
```

## ✅ Requirements
- **Python**: 3.10 or higher
- **MySQL Server**: 8.0 or higher
- **pip**: Python package installer
- **MySQL client**: Command line tool (`mysql`)

## ⚙️ Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/alessandrorebosio/DB25-farmhouse.git
cd DB25-farmhouse
```

### 2. Create Virtual Environment (Recommended)
```bash
python -m venv venv
source venv/bin/activate     # macOS/Linux
# venv\Scripts\activate      # Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Setup
**Create MySQL Database:**
```bash
mysql -u root -p < app/sql/db.sql
```

## 🚀 Running the Application

### Start Development Server
```bash
cd app
python manage.py runserver
```

The application will be available at: **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

## 📦 Dependencies
The project uses the following main dependencies (see `requirements.txt`):
- **Django 5.2.4**: Web framework
- **mysqlclient 2.2.7**: MySQL database adapter
- **asgiref 3.9.1**: ASGI utilities
- **sqlparse 0.5.3**: SQL parsing library

## 👥 Team Members

### Maisam Noumi
- **GitHub**: [@ennoumi](https://github.com/ennoumi)
- **Email**: [maisam.noumi@studio.unibo.it](mailto:maisam.noumi@studio.unibo.it)

### Alessandro Rebosio
- **GitHub**: [@alessandrorebosio](https://github.com/alessandrorebosio)
- **Email**: [alessandro.rebosio@studio.unibo.it](mailto:alessandro.rebosio@studio.unibo.it)

### Filippo Ricciotti
- **GitHub**: [@Riccio-15](https://github.com/Riccio-15)
- **Email**: [filippo.ricciotti@studio.unibo.it](mailto:filippo.ricciotti@studio.unibo.it)

