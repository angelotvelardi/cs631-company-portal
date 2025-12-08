# routes/divisions.py
from flask import Blueprint, render_template, request, redirect, url_for
from models import db, Division

bp = Blueprint("divisions", __name__, url_prefix="/divisions")


@bp.route("/")
def list_divisions():
    divisions = Division.query.order_by(Division.Division_Name).all()
    return render_template("divisions/list.html", divisions=divisions)


@bp.route("/create", methods=["GET", "POST"])
def create_division():
    if request.method == "POST":
        name = request.form.get("Division_Name", "").strip()
        if not name:
            return render_template(
                "divisions/create.html",
                error="Division name is required.",
            )
        existing = Division.query.get(name)
        if existing:
            return render_template(
                "divisions/create.html",
                error="Division with that name already exists.",
            )

        division = Division(Division_Name=name)
        db.session.add(division)
        db.session.commit()
        return redirect(url_for("divisions.list_divisions"))

    return render_template("divisions/create.html")


@bp.route("/<division_name>/edit", methods=["GET", "POST"])
def edit_division(division_name):
    division = Division.query.get_or_404(division_name)

    if request.method == "POST":
        # We don't let them change the PK, just other fields later if you add any.
        # For now Division has only Division_Name + Head_Emp_No (not used on form).
        # So this is mostly a placeholder in case you add fields later.
        return redirect(url_for("divisions.list_divisions"))

    return render_template("divisions/edit.html", division=division)


@bp.route("/<division_name>/delete", methods=["POST"])
def delete_division(division_name):
    division = Division.query.get_or_404(division_name)
    db.session.delete(division)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        # optional: flash/return an error if there are FK dependencies
    return redirect(url_for("divisions.list_divisions"))
