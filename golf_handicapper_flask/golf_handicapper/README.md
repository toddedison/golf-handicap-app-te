# Golf Handicapper – Flask

A full rewrite of the Ruby on Rails Golf Handicapper app in Python/Flask.

## Features
- User registration with email activation
- Secure login with "remember me" / persistent sessions
- Password reset by email (2-hour expiry)
- Add / delete rounds (course, date, score, slope, course rating)
- USGA handicap index calculation
- Printable PDF scorecard export
- Admin panel to list / delete users

## Setup

```bash
# 1 – Create a virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 2 – Install dependencies
pip install -r requirements.txt

# 3 – Create a .env file (copy from below and fill in values)
cp .env.example .env

# 4 – Initialise the database
flask --app run db init
flask --app run db migrate -m "initial"
flask --app run db upgrade

# 5 – Run the dev server
flask --app run run --debug
```

## Environment Variables (.env)

```
SECRET_KEY=your-very-secret-key
DATABASE_URL=sqlite:///golf_handicapper.db   # or postgresql://...
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your@gmail.com
MAIL_PASSWORD=app-password
MAIL_DEFAULT_SENDER=noreply@golfhandicapper.com
```

## Project Structure

```
golf_handicapper/
├── __init__.py          # App factory + extensions
├── config.py            # Config class
├── models.py            # User + Round models
├── forms.py             # WTForms form classes
├── email.py             # Email sending helpers
├── pdf_export.py        # ReportLab PDF generation
├── routes/
│   ├── auth.py          # Login, signup, activation, password reset
│   ├── users.py         # Profile show, edit, admin index
│   ├── rounds.py        # Add / delete rounds
│   └── static_pages.py  # Home, about, help, privacy
└── templates/
    ├── base.html
    ├── auth/
    ├── users/
    ├── rounds/
    ├── static_pages/
    └── email/
```

## Rails → Flask Mapping

| Rails | Flask |
|---|---|
| `ApplicationRecord` | SQLAlchemy `db.Model` |
| `User` model | `models.py` → `User` |
| `Micropost` model | `models.py` → `Round` |
| `SessionsController` | `routes/auth.py` – login/logout |
| `UsersController` | `routes/users.py` |
| `MicropostsController` | `routes/rounds.py` |
| `AccountActivationsController` | `routes/auth.py` – `activate()` |
| `PasswordResetsController` | `routes/auth.py` – password reset |
| `LandingPagesController` | `routes/static_pages.py` |
| `has_secure_password` | Flask-Bcrypt |
| `before_action :logged_in_user` | `@login_required` |
| `flash[:success]` | `flash('msg', 'success')` |
| ERB templates | Jinja2 templates |
| `ScorecardPdf` (Prawn) | `pdf_export.py` (ReportLab) |
