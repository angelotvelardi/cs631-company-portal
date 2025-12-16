from flask import Blueprint, render_template, request, redirect, url_for
from datetime import datetime
from models import db, ProjectEmployee, Employee, Project

bp = Blueprint("project_employees", __name__, url_prefix="/project-employees")


@bp.route("/")
def list_project_employees():
    rows = (
        db.session.query(ProjectEmployee, Employee, Project)
        .join(Employee, ProjectEmployee.Employee_No == Employee.Employee_No)
        .join(Project, ProjectEmployee.Project_Number == Project.Project_Number)
        .order_by(Employee.Employee_Name)
        .all()
    )
    return render_template("project_employees/list.html", rows=rows)


@bp.route("/create", methods=["GET", "POST"])
def create_project_employee():
    employees = Employee.query.order_by(Employee.Employee_Name).all()
    projects = Project.query.order_by(Project.Project_Number).all()

    if request.method == "POST":
        emp_no = request.form.get("Employee_No")
        proj_no = request.form.get("Project_Number")
        hourly_rate = request.form.get("Hourly_Rate", "").strip()
        start_str = request.form.get("Start_Date", "").strip()
        end_str = request.form.get("End_Date", "").strip()

        if not emp_no or not proj_no or not hourly_rate or not start_str:
            return render_template(
                "project_employees/create.html",
                employees=employees,
                projects=projects,
                error="Employee, project, hourly rate, and start date are required.",
            )

        if ProjectEmployee.query.get(int(emp_no)):
            return render_template(
                "project_employees/create.html",
                employees=employees,
                projects=projects,
                error="This employee already has an hourly project contract.",
            )

        try:
            start_date = datetime.strptime(start_str, "%Y-%m-%d").date()
        except ValueError:
            return render_template(
                "project_employees/create.html",
                employees=employees,
                projects=projects,
                error="Start date must be YYYY-MM-DD.",
            )

        end_date = None
        if end_str:
            try:
                end_date = datetime.strptime(end_str, "%Y-%m-%d").date()
            except ValueError:
                return render_template(
                    "project_employees/create.html",
                    employees=employees,
                    projects=projects,
                    error="End date must be YYYY-MM-DD.",
                )

        pe = ProjectEmployee(
            Employee_No=int(emp_no),
            Project_Number=int(proj_no),
            Hourly_Rate=hourly_rate,
            Start_Date=start_date,
            End_Date=end_date,
        )
        db.session.add(pe)
        db.session.commit()
        return redirect(url_for("project_employees.list_project_employees"))

    return render_template("project_employees/create.html", employees=employees, projects=projects)


@bp.route("/<int:employee_no>/edit", methods=["GET", "POST"])
def edit_project_employee(employee_no):
    pe = ProjectEmployee.query.get_or_404(employee_no)
    projects = Project.query.order_by(Project.Project_Number).all()

    if request.method == "POST":
        proj_no = request.form.get("Project_Number")
        hourly_rate = request.form.get("Hourly_Rate", "").strip()
        start_str = request.form.get("Start_Date", "").strip()
        end_str = request.form.get("End_Date", "").strip()

        if not proj_no or not hourly_rate or not start_str:
            return render_template(
                "project_employees/edit.html",
                pe=pe,
                projects=projects,
                error="Project, hourly rate, and start date are required.",
            )

        try:
            start_date = datetime.strptime(start_str, "%Y-%m-%d").date()
        except ValueError:
            return render_template(
                "project_employees/edit.html",
                pe=pe,
                projects=projects,
                error="Start date must be YYYY-MM-DD.",
            )

        end_date = None
        if end_str:
            try:
                end_date = datetime.strptime(end_str, "%Y-%m-%d").date()
            except ValueError:
                return render_template(
                    "project_employees/edit.html",
                    pe=pe,
                    projects=projects,
                    error="End date must be YYYY-MM-DD.",
                )

        pe.Project_Number = int(proj_no)
        pe.Hourly_Rate = hourly_rate
        pe.Start_Date = start_date
        pe.End_Date = end_date

        db.session.commit()
        return redirect(url_for("project_employees.list_project_employees"))

    return render_template("project_employees/edit.html", pe=pe, projects=projects)


@bp.route("/<int:employee_no>/delete", methods=["POST"])
def delete_project_employee(employee_no):
    pe = ProjectEmployee.query.get_or_404(employee_no)
    db.session.delete(pe)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
    return redirect(url_for("project_employees.list_project_employees"))
