# routes/departments.py
from flask import Blueprint, render_template, request, redirect, url_for
from models import db, Department, Division

bp = Blueprint("departments", __name__, url_prefix="/departments")


@bp.route("/")
def list_departments():
    departments = (
        db.session.query(Department, Division)
        .join(Division, Department.Division_Name == Division.Division_Name)
        .order_by(Department.Department_Name)
        .all()
    )
    return render_template("departments/list.html", departments=departments)


@bp.route("/create", methods=["GET", "POST"])
def create_department():
    divisions = Division.query.order_by(Division.Division_Name).all()

    if request.method == "POST":
        name = request.form.get("Department_Name", "").strip()
        budget = request.form.get("Budget", "").strip()
        division_name = request.form.get("Division_Name")

        if not name or not division_name:
            return render_template(
                "departments/create.html",
                divisions=divisions,
                error="Department name and division are required.",
            )

        existing = Department.query.get(name)
        if existing:
            return render_template(
                "departments/create.html",
                divisions=divisions,
                error="Department with that name already exists.",
            )

        dept = Department(
            Department_Name=name,
            Budget=budget or None,
            Division_Name=division_name,
        )
        db.session.add(dept)
        db.session.commit()
        return redirect(url_for("departments.list_departments"))

    return render_template("departments/create.html", divisions=divisions)


@bp.route("/<department_name>/edit", methods=["GET", "POST"])
def edit_department(department_name):
    dept = Department.query.get_or_404(department_name)
    divisions = Division.query.order_by(Division.Division_Name).all()

    if request.method == "POST":
        budget = request.form.get("Budget", "").strip()
        division_name = request.form.get("Division_Name")

        if not division_name:
            return render_template(
                "departments/edit.html",
                department=dept,
                divisions=divisions,
                error="Division is required.",
            )

        dept.Budget = budget or None
        dept.Division_Name = division_name

        db.session.commit()
        return redirect(url_for("departments.list_departments"))

    return render_template(
        "departments/edit.html",
        department=dept,
        divisions=divisions,
    )


@bp.route("/<department_name>/delete", methods=["POST"])
def delete_department(department_name):
    dept = Department.query.get_or_404(department_name)
    db.session.delete(dept)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
    return redirect(url_for("departments.list_departments"))
