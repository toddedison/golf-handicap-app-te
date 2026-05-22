from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user

from .. import db
from ..models import Round
from ..forms import RoundForm

rounds_bp = Blueprint('rounds', __name__, url_prefix='/rounds')


@rounds_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    form = RoundForm()
    if form.validate_on_submit():
        r = Round(
            user_id   = current_user.id,
            course    = form.course.data,
            game_date = form.game_date.data,
            slope     = form.slope.data,
            rating    = form.rating.data,
            score     = form.score.data,
        )
        db.session.add(r)
        db.session.commit()
        flash('Round saved!', 'success')
        return redirect(url_for('users.show', user_id=current_user.id))
    if form.errors:
        flash('Error saving round!', 'danger')
    return render_template('rounds/new.html', form=form)


@rounds_bp.route('/<int:round_id>/delete', methods=['POST'])
@login_required
def delete(round_id):
    r = Round.query.get_or_404(round_id)
    if r.user_id != current_user.id and not current_user.admin:
        flash('Access denied!', 'danger')
        return redirect(url_for('users.show', user_id=current_user.id))
    db.session.delete(r)
    db.session.commit()
    flash('Round deleted!', 'success')
    return redirect(url_for('users.show', user_id=current_user.id))
