# routes/workson.py
from flask import Blueprint, render_template, request, redirect, url_for
from models import db, Works_On, Employee, Project

bp = Blueprint("workson", __name__, url_prefix="/workson")


@bp.route("/")
def list_workson():
    rows = (
        db.session.query(Works_On, Employee, Project)
        .join(Employee, Works_On.Employee_No == Employee.Employee_No)
        .join(Project, Works_On.Project_Number == Project.Project_Number)
        .order_by(Employee.Employee_Name, Project.Project_Number)
        .all()
    )
    return render_template("workson/list.html", rows=rows)


@bp.route("/create", methods=["GET", "POST"])
def create_workson():
    employees = Employee.query.order_by(Employee.Employee_Name).all()
    projects = Project.query.order_by(Project.Project_Number).all()

    if request.method == "POST":
        emp_no = request.form.get("Employee_No")
        proj_no = request.form.get("Project_Number")
        time_spent = request.form.get("Time_Spent", "").strip()
        role = request.form.get("Role", "").strip()

        if not emp_no or not proj_no:
            return render_template(
                "workson/create.html",
                employees=employees,
                projects=projects,
                error="Employee and project are required.",
            )

        existing = Works_On.query.get((int(emp_no), int(proj_no)))
        if existing:
            return render_template(
                "workson/create.html",
                employees=employees,
                projects=projects,
                error="This employee is already assigned to that project.",
            )

        row = Works_On(
            Employee_No=int(emp_no),
            Project_Number=int(proj_no),
            Time_Spent=time_spent or None,
            Role=role or None,
        )
        db.session.add(row)
        db.session.commit()
        return redirect(url_for("workson.list_workson"))

    return render_template(
        "workson/create.html",
        employees=employees,
        projects=projects,
    )


@bp.route("/<int:employee_no>/<int:project_number>/edit", methods=["GET", "POST"])
def edit_workson(employee_no, project_number):
    row = Works_On.query.get_or_404((employee_no, project_number))

    if request.method == "POST":
        time_spent = request.form.get("Time_Spent", "").strip()
        role = request.form.get("Role", "").strip()

        row.Time_Spent = time_spent or None
        row.Role = role or None

        db.session.commit()
        return redirect(url_for("workson.list_workson"))

    return render_template("workson/edit.html", workson=row)


@bp.route("/<int:employee_no>/<int:project_number>/delete", methods=["POST"])
def delete_workson(employee_no, project_number):
    row = Works_On.query.get_or_404((employee_no, project_number))
    db.session.delete(row)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
    return redirect(url_for("workson.list_workson"))
