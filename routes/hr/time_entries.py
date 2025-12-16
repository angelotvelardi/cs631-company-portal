from flask import Blueprint, render_template, request, redirect, url_for
from datetime import datetime
from models import db, TimeEntry, Employee, Project

bp = Blueprint("time_entries", __name__, url_prefix="/time-entries")


@bp.route("/")
def list_time_entries():
    rows = (
        db.session.query(TimeEntry, Employee, Project)
        .join(Employee, TimeEntry.Employee_No == Employee.Employee_No)
        .join(Project, TimeEntry.Project_Number == Project.Project_Number)
        .order_by(TimeEntry.Work_Date.desc())
        .all()
    )
    return render_template("time_entries/list.html", rows=rows)


@bp.route("/create", methods=["GET", "POST"])
def create_time_entry():
    employees = Employee.query.order_by(Employee.Employee_Name).all()
    projects = Project.query.order_by(Project.Project_Number).all()

    if request.method == "POST":
        emp_no = request.form.get("Employee_No")
        proj_no = request.form.get("Project_Number")
        work_date_str = request.form.get("Work_Date", "").strip()
        hours_str = request.form.get("Hours", "").strip()

        if not emp_no or not proj_no or not work_date_str or not hours_str:
            return render_template(
                "time_entries/create.html",
                employees=employees,
                projects=projects,
                error="Employee, project, work date, and hours are required.",
            )

        try:
            work_date = datetime.strptime(work_date_str, "%Y-%m-%d").date()
        except ValueError:
            return render_template(
                "time_entries/create.html",
                employees=employees,
                projects=projects,
                error="Work date must be YYYY-MM-DD.",
            )

        te = TimeEntry(
            Employee_No=int(emp_no),
            Project_Number=int(proj_no),
            Work_Date=work_date,
            Hours=hours_str,
        )
        db.session.add(te)
        db.session.commit()
        return redirect(url_for("time_entries.list_time_entries"))

    return render_template("time_entries/create.html", employees=employees, projects=projects)


@bp.route("/<int:time_entry_id>/edit", methods=["GET", "POST"])
def edit_time_entry(time_entry_id):
    te = TimeEntry.query.get_or_404(time_entry_id)
    employees = Employee.query.order_by(Employee.Employee_Name).all()
    projects = Project.query.order_by(Project.Project_Number).all()

    if request.method == "POST":
        emp_no = request.form.get("Employee_No")
        proj_no = request.form.get("Project_Number")
        work_date_str = request.form.get("Work_Date", "").strip()
        hours_str = request.form.get("Hours", "").strip()

        if not emp_no or not proj_no or not work_date_str or not hours_str:
            return render_template(
                "time_entries/edit.html",
                te=te,
                employees=employees,
                projects=projects,
                error="All fields are required.",
            )

        try:
            work_date = datetime.strptime(work_date_str, "%Y-%m-%d").date()
        except ValueError:
            return render_template(
                "time_entries/edit.html",
                te=te,
                employees=employees,
                projects=projects,
                error="Work date must be YYYY-MM-DD.",
            )

        te.Employee_No = int(emp_no)
        te.Project_Number = int(proj_no)
        te.Work_Date = work_date
        te.Hours = hours_str

        db.session.commit()
        return redirect(url_for("time_entries.list_time_entries"))

    return render_template("time_entries/edit.html", te=te, employees=employees, projects=projects)


@bp.route("/<int:time_entry_id>/delete", methods=["POST"])
def delete_time_entry(time_entry_id):
    te = TimeEntry.query.get_or_404(time_entry_id)
    db.session.delete(te)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
    return redirect(url_for("time_entries.list_time_entries"))
