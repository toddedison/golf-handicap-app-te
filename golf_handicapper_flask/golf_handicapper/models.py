import secrets
from datetime import datetime, timezone, timedelta

from flask import current_app
from flask_login import UserMixin
from werkzeug.utils import secure_filename

from . import db, bcrypt, login_manager


# ---------------------------------------------------------------------------
# Flask-Login user loader
# ---------------------------------------------------------------------------
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ---------------------------------------------------------------------------
# User model  (was user.rb)
# ---------------------------------------------------------------------------
class User(db.Model, UserMixin):
    __tablename__ = 'users'

    # USGA adjustment factor (same as Ruby constant)
    BETTER_GOLFER_NARROW_BELL_CURVE_VALUE = 0.96

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    picture = db.Column(db.String(255))          # relative path to uploaded file

    # Account activation
    activated = db.Column(db.Boolean, default=False, nullable=False)
    activated_at = db.Column(db.DateTime)
    activation_digest = db.Column(db.String(128))

    # Password reset
    reset_digest = db.Column(db.String(128))
    reset_sent_at = db.Column(db.DateTime)

    # Persistent "remember me" session
    remember_digest = db.Column(db.String(128))

    # Admin flag
    admin = db.Column(db.Boolean, default=False, nullable=False)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    rounds = db.relationship('Round', backref='user', lazy='dynamic',
                             cascade='all, delete-orphan',
                             order_by='Round.game_date.desc()')

    # ------------------------------------------------------------------
    # Password helpers
    # ------------------------------------------------------------------
    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    # ------------------------------------------------------------------
    # Token helpers  (mirrors User.new_token / User.digest)
    # ------------------------------------------------------------------
    @staticmethod
    def new_token():
        return secrets.token_urlsafe()

    @staticmethod
    def digest(token):
        return bcrypt.generate_password_hash(token).decode('utf-8')

    def authenticated(self, attribute, token):
        """Check that *token* matches the stored *attribute*_digest."""
        digest = getattr(self, f'{attribute}_digest', None)
        if not digest:
            return False
        return bcrypt.check_password_hash(digest, token)

    # ------------------------------------------------------------------
    # Persistent sessions
    # ------------------------------------------------------------------
    def remember(self):
        token = User.new_token()
        self.remember_digest = User.digest(token)
        db.session.commit()
        return token

    def forget(self):
        self.remember_digest = None
        db.session.commit()

    # ------------------------------------------------------------------
    # Account activation
    # ------------------------------------------------------------------
    def create_activation_digest(self):
        token = User.new_token()
        self.activation_digest = User.digest(token)
        return token     # caller stores this in the email link

    def activate(self):
        self.activated = True
        self.activated_at = datetime.now(timezone.utc)
        db.session.commit()

    # ------------------------------------------------------------------
    # Password reset
    # ------------------------------------------------------------------
    def create_reset_digest(self):
        token = User.new_token()
        self.reset_digest = User.digest(token)
        self.reset_sent_at = datetime.now(timezone.utc)
        db.session.commit()
        return token

    def password_reset_expired(self):
        if not self.reset_sent_at:
            return True
        expiry = self.reset_sent_at.replace(tzinfo=timezone.utc) + timedelta(hours=2)
        return datetime.now(timezone.utc) > expiry

    # ------------------------------------------------------------------
    # Handicap calculation  (direct port from user.rb)
    # ------------------------------------------------------------------
    @property
    def handicap(self):
        diffs = [self._round_differential(r) for r in self.rounds]
        return self._average_handicap(diffs)

    def _round_differential(self, round_):
        return round((round_.score - round_.rating) * 113 / round_.slope, 1)

    def _calculate_average(self, diffs, divisor):
        return sum(sorted(diffs)[:divisor]) / divisor

    def _average_handicap(self, diffs):
        n = len(diffs)
        divisor_map = {
            range(0, 7):  1,
            range(7, 10): 2,
            range(10, 12): 3,
            range(12, 14): 4,
            range(14, 16): 5,
            range(16, 18): 6,
            range(18, 19): 7,
            range(19, 20): 8,
            range(20, 21): 9,
            range(21, 22): 10,
        }
        divisor = 0
        for r, d in divisor_map.items():
            if n in r:
                divisor = d
                break
        if n > 21:
            divisor = 10
        if divisor == 0:
            return 0.0
        raw = self._calculate_average(diffs, divisor)
        return round(raw * self.BETTER_GOLFER_NARROW_BELL_CURVE_VALUE, 1)

    def __repr__(self):
        return f'<User {self.email}>'


# ---------------------------------------------------------------------------
# Round model  (was micropost.rb — renamed for clarity)
# ---------------------------------------------------------------------------
class Round(db.Model):
    __tablename__ = 'rounds'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    course = db.Column(db.String(40), nullable=False)
    game_date = db.Column(db.String(40), nullable=False)
    slope = db.Column(db.Float, nullable=False)     # 55–155, 2–3 digits
    rating = db.Column(db.Float, nullable=False)    # e.g. 72.4, 2–4 digits
    score = db.Column(db.Integer, nullable=False)   # gross score

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f'<Round {self.course} {self.game_date}>'
