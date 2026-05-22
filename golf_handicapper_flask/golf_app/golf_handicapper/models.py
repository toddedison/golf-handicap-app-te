import os, secrets
from datetime import datetime, timezone, timedelta
from flask_login import UserMixin
from . import db, bcrypt, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    BELL_CURVE = 0.96   # BETTER_GOLFER_NARROW_BELL_CURVE_VALUE

    id               = db.Column(db.Integer, primary_key=True)
    name             = db.Column(db.String(50),  nullable=False)
    email            = db.Column(db.String(255), nullable=False, unique=True, index=True)
    password_hash    = db.Column(db.String(128), nullable=False)
    picture          = db.Column(db.String(255))

    activated        = db.Column(db.Boolean, default=False, nullable=False)
    activated_at     = db.Column(db.DateTime)
    activation_digest = db.Column(db.String(128))

    reset_digest     = db.Column(db.String(128))
    reset_sent_at    = db.Column(db.DateTime)

    remember_digest  = db.Column(db.String(128))
    admin            = db.Column(db.Boolean, default=False, nullable=False)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    rounds = db.relationship('Round', backref='user', lazy='dynamic',
                             cascade='all, delete-orphan',
                             order_by='Round.created_at.desc()')

    # ── password ────────────────────────────────────────────────────────
    def set_password(self, pw):
        self.password_hash = bcrypt.generate_password_hash(pw).decode('utf-8')

    def check_password(self, pw):
        return bcrypt.check_password_hash(self.password_hash, pw)

    # ── tokens ──────────────────────────────────────────────────────────
    @staticmethod
    def new_token():
        return secrets.token_urlsafe()

    @staticmethod
    def digest(token):
        return bcrypt.generate_password_hash(token).decode('utf-8')

    def authenticated(self, attribute, token):
        digest = getattr(self, f'{attribute}_digest', None)
        if not digest:
            return False
        return bcrypt.check_password_hash(digest, token)

    # ── remember me ─────────────────────────────────────────────────────
    def remember(self):
        token = User.new_token()
        self.remember_digest = User.digest(token)
        db.session.commit()
        return token

    def forget(self):
        self.remember_digest = None
        db.session.commit()

    # ── activation ──────────────────────────────────────────────────────
    def create_activation_digest(self):
        token = User.new_token()
        self.activation_digest = User.digest(token)
        return token

    def activate(self):
        self.activated    = True
        self.activated_at = datetime.now(timezone.utc)
        db.session.commit()

    # ── password reset ───────────────────────────────────────────────────
    def create_reset_digest(self):
        token = User.new_token()
        self.reset_digest  = User.digest(token)
        self.reset_sent_at = datetime.now(timezone.utc)
        db.session.commit()
        return token

    def password_reset_expired(self):
        if not self.reset_sent_at:
            return True
        sent = self.reset_sent_at.replace(tzinfo=timezone.utc)
        return datetime.now(timezone.utc) > sent + timedelta(hours=2)

    # ── handicap calculation (direct port of user.rb) ────────────────────
    @property
    def handicap(self):
        diffs = [round((r.score - r.rating) * 113 / r.slope, 1)
                 for r in self.rounds]
        return self._average_handicap(diffs)

    def _average_handicap(self, diffs):
        n = len(diffs)
        # Mirrors the Ruby case/when table
        if   n <= 6:  divisor = 1
        elif n <= 9:  divisor = 2
        elif n <= 11: divisor = 3
        elif n <= 13: divisor = 4
        elif n <= 15: divisor = 5
        elif n <= 17: divisor = 6
        elif n == 17: divisor = 7   # never reached due to above, kept for parity
        elif n == 18: divisor = 8
        elif n == 19: divisor = 9
        elif n == 20: divisor = 10
        else:         divisor = 0
        if divisor == 0:
            return 0.0
        avg = sum(sorted(diffs)[:divisor]) / divisor
        return round(avg * self.BELL_CURVE, 1)

    def picture_url(self):
        if self.picture:
            return f'/static/img/{self.picture}'
        return None

    def __repr__(self):
        return f'<User {self.email}>'


class Round(db.Model):
    __tablename__ = 'rounds'

    id        = db.Column(db.Integer, primary_key=True)
    user_id   = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course    = db.Column(db.String(40),  nullable=False)
    game_date = db.Column(db.String(40),  nullable=False)
    slope     = db.Column(db.Float,       nullable=False)
    rating    = db.Column(db.Float,       nullable=False)
    score     = db.Column(db.Integer,     nullable=False)
    created_at = db.Column(db.DateTime,   default=lambda: datetime.now(timezone.utc))

    def differential(self):
        return round((self.score - self.rating) * 113 / self.slope, 1)

    def __repr__(self):
        return f'<Round {self.course} {self.game_date}>'
