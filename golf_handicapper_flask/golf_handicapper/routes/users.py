import os
from flask import (Blueprint, render_template, redirect, url_for,
                   flash, request, current_app, abort, send_file)
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from .. import db
from ..models import User
from ..forms import EditProfileForm

users_bp = Blueprint('users', __name__, url_prefix='/users')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def _allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def _save_picture(file_storage):
    filename = secure_filename(file_storage.filename)
    upload_folder = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_folder, exist_ok=True)
    filepath = os.path.join(upload_folder, filename)
    file_storage.save(filepath)
    return filename


# ---------------------------------------------------------------------------
# Admin: list all users
# ---------------------------------------------------------------------------
@users_bp.route('/')
@login_required
def index():
    if not current_user.admin:
        abort(403)
    page = request.args.get('page', 1, type=int)
    pagination = User.query.order_by(User.created_at.desc()).paginate(
        page=page,
        per_page=current_app.config.get('USERS_PER_PAGE', 30),
        error_out=False
    )
    return render_template('users/index.html', pagination=pagination)


# ---------------------------------------------------------------------------
# User profile / scorecard
# ---------------------------------------------------------------------------
@users_bp.route('/<int:user_id>')
@login_required
def show(user_id):
    user = User.query.get_or_404(user_id)
    # Only self or admin can view
    if user != current_user and not current_user.admin:
        flash('Access denied!', 'danger')
        return redirect(url_for('users.show', user_id=current_user.id))

    # PDF export
    if request.args.get('format') == 'pdf':
        from ..pdf_export import generate_scorecard_pdf
        pdf_bytes = generate_scorecard_pdf(user)
        from io import BytesIO
        return send_file(
            BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=False,
            download_name=f'Golf-Handicap-{user.name}.pdf'
        )

    rounds = user.rounds.all()
    return render_template('users/show.html', user=user, rounds=rounds)


# ---------------------------------------------------------------------------
# Edit profile
# ---------------------------------------------------------------------------
@users_bp.route('/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(user_id):
    user = User.query.get_or_404(user_id)
    if user != current_user:
        abort(403)
    form = EditProfileForm(obj=user)
    if form.validate_on_submit():
        user.name = form.name.data
        user.email = form.email.data.lower()
        if form.password.data:
            user.set_password(form.password.data)
        if form.picture.data and _allowed_file(form.picture.data.filename):
            filename = _save_picture(form.picture.data)
            user.picture = filename
        db.session.commit()
        flash('Profile updated', 'success')
        return redirect(url_for('users.show', user_id=user.id))
    return render_template('users/edit.html', form=form, user=user)


# ---------------------------------------------------------------------------
# Delete user (admin only)
# ---------------------------------------------------------------------------
@users_bp.route('/<int:user_id>/delete', methods=['POST'])
@login_required
def delete(user_id):
    if not current_user.admin:
        abort(403)
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('User deleted!', 'success')
    return redirect(url_for('users.index'))
