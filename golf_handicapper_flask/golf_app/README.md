# The Golf Handicapper — Flask

Full Python/Flask rewrite of the Ruby on Rails Golf Handicapper app.

## Quick Start

```bash
# 1. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Copy and fill in your environment variables
cp .env.example .env            # then edit .env

# 4. Initialise the database
flask --app run db init
flask --app run db migrate -m "initial schema"
flask --app run db upgrade

# 5. Run the dev server
flask --app run run --debug
```

## Environment Variables (.env)

```
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///golf_handicapper.db   # or postgresql://...
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=you@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=noreply@golfhandicapper.com
```

## Project Layout

```
golf_app/
├── run.py                     # Flask entry point
├── config.py                  # Configuration
├── requirements.txt
└── golf_handicapper/
    ├── __init__.py            # App factory + extensions
    ├── models.py              # User + Round (SQLAlchemy)
    ├── forms.py               # WTForms
    ├── email.py               # Flask-Mail helpers
    ├── pdf_export.py          # ReportLab PDF (replaces Prawn)
    ├── routes/
    │   ├── static_pages.py    # LandingPagesController
    │   ├── auth.py            # Sessions + Activations + PasswordResets
    │   ├── users.py           # UsersController
    │   └── rounds.py          # MicropostsController
    ├── static/
    │   ├── css/app.css
    │   ├── js/app.js
    │   └── img/               # ← copy your images here
    └── templates/
        ├── base.html          # application_html.erb + header + footer
        ├── shared/
        │   └── _error_messages.html
        ├── static_pages/      # home, about, help, privacy, contact
        ├── auth/              # login, signup, password reset
        ├── users/             # show (scorecard), edit, index (admin)
        ├── rounds/            # new round form
        └── email/             # activation + password reset emails
```

## Image Assets

Copy these from the original Rails `app/assets/images/` folder into
`golf_handicapper/static/img/`:

- `golf-background2.jpg`
- `putting.jpg`
- `golf-shot.jpg`
- `handicap-differentials.png`
- `handicap-differential-calculation.png`
- `Family_Portrait_Best.gif`

## Rails → Flask Mapping

| Rails | Flask |
|---|---|
| `User` model | `models.py → User` |
| `Micropost` model | `models.py → Round` |
| `has_secure_password` | Flask-Bcrypt |
| `before_action :logged_in_user` | `@login_required` |
| `SessionsController` | `routes/auth.py` |
| `AccountActivationsController` | `routes/auth.py → activate()` |
| `PasswordResetsController` | `routes/auth.py → password_reset*()` |
| `UsersController` | `routes/users.py` |
| `MicropostsController` | `routes/rounds.py` |
| `LandingPagesController` | `routes/static_pages.py` |
| ERB templates | Jinja2 templates |
| `ScorecardPdf` (Prawn) | `pdf_export.py` (ReportLab) |
| `will_paginate` | SQLAlchemy `.paginate()` |
| `flash[:success]` | `flash('msg', 'success')` |
