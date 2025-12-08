# routes/titles.py
from flask import Blueprint, render_template, request, redirect, url_for
from models import db, Employee_Title

bp = Blueprint("titles", __name__, url_prefix="/titles")


@bp.route("/")
def list_titles():
    titles = Employee_Title.query.order_by(Employee_Title.Title).all()
    return render_template("titles/list.html", titles=titles)


@bp.route("/create", methods=["GET", "POST"])
def create_title():
    if request.method == "POST":
        title_name = request.form.get("Title", "").strip()
        salary_str = request.form.get("Salary", "").strip()

        if not title_name:
            return render_template(
                "titles/create.html",
                error="Title name is required.",
            )

        existing = Employee_Title.query.get(title_name)
        if existing:
            return render_template(
                "titles/create.html",
                error="A title with that name already exists.",
            )

        salary = salary_str or None

        t = Employee_Title(
            Title=title_name,
            Salary=salary,
        )
        db.session.add(t)
        db.session.commit()
        return redirect(url_for("titles.list_titles"))

    return render_template("titles/create.html")


@bp.route("/<title_name>/edit", methods=["GET", "POST"])
def edit_title(title_name):
    t = Employee_Title.query.get_or_404(title_name)

    if request.method == "POST":
        salary_str = request.form.get("Salary", "").strip()
        t.Salary = salary_str or None
        db.session.commit()
        return redirect(url_for("titles.list_titles"))

    return render_template("titles/edit.html", title_obj=t)


@bp.route("/<title_name>/delete", methods=["POST"])
def delete_title(title_name):
    t = Employee_Title.query.get_or_404(title_name)
    db.session.delete(t)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        # if FK constraints (employees using this title), delete will fail
        # you could add flash message here if you wire up flashing
    return redirect(url_for("titles.list_titles"))
