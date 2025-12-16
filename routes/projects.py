# routes/projects.py
from flask import Blueprint, render_template, request, redirect, url_for
from models import db, Project, Department, Employee, Works_On, TimeEntry, ProjectMilestone
from datetime import datetime

bp = Blueprint("projects", __name__, url_prefix="/projects")


@bp.route("/")
def list_projects():
    projects = (
        db.session.query(Project, Department, Employee)
        .join(Department, Project.Department_Name == Department.Department_Name)
        .join(Employee, Project.Manager_Emp_No == Employee.Employee_No)
        .order_by(Project.Project_Number)
        .all()
    )
    return render_template("projects/list.html", projects=projects)


@bp.route("/create", methods=["GET", "POST"])
def create_project():
    departments = Department.query.order_by(Department.Department_Name).all()
    employees = Employee.query.order_by(Employee.Employee_Name).all()

    if request.method == "POST":
        proj_no_str = request.form.get("Project_Number", "").strip()
        budget = request.form.get("Budget", "").strip()
        start_date_str = request.form.get("Date_Started", "").strip()
        end_date_str = request.form.get("Date_Ended", "").strip()
        dept_name = request.form.get("Department_Name")
        manager_emp_no = request.form.get("Manager_Emp_No")
        team = request.form.getlist("Team_Employee_Nos")

        if not proj_no_str or not dept_name or not manager_emp_no:
            return render_template(
                "projects/create.html",
                departments=departments,
                employees=employees,
                error="Project number, department, and manager are required.",
            )

        try:
            proj_no = int(proj_no_str)
        except ValueError:
            return render_template(
                "projects/create.html",
                departments=departments,
                employees=employees,
                error="Project number must be an integer.",
            )

        if Project.query.get(proj_no):
            return render_template(
                "projects/create.html",
                departments=departments,
                employees=employees,
                error="A project with that number already exists.",
            )

        start_date = None
        end_date = None
        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            except ValueError:
                return render_template(
                    "projects/create.html",
                    departments=departments,
                    employees=employees,
                    error="Invalid start date.",
                )
        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
            except ValueError:
                return render_template(
                    "projects/create.html",
                    departments=departments,
                    employees=employees,
                    error="Invalid end date.",
                )

        project = Project(
            Project_Number=proj_no,
            Budget=budget or None,
            Date_Started=start_date,
            Date_Ended=end_date,
            Department_Name=dept_name,
            Manager_Emp_No=int(manager_emp_no),
        )
        db.session.add(project)
        db.session.commit()

        if str(manager_emp_no) not in team:
            team.append(str(manager_emp_no))

        for emp_no_str in team:
            wo = Works_On(
                Employee_No=int(emp_no_str),
                Project_Number=project.Project_Number,
                Time_Spent=None,
                Role=None
            )
            existing = Works_On.query.get((wo.Employee_No, wo.Project_Number))
            if not existing:
                db.session.add(wo)

        db.session.commit()

        return redirect(url_for("projects.list_projects"))

    return render_template("projects/create.html", departments=departments, employees=employees)


@bp.route("/<int:project_number>/edit", methods=["GET", "POST"])
def edit_project(project_number):
    proj = Project.query.get_or_404(project_number)
    departments = Department.query.order_by(Department.Department_Name).all()
    employees = Employee.query.order_by(Employee.Employee_Name).all()

    if request.method == "POST":
        budget = request.form.get("Budget", "").strip()
        start_date_str = request.form.get("Date_Started", "").strip()
        end_date_str = request.form.get("Date_Ended", "").strip()
        dept_name = request.form.get("Department_Name")
        manager_emp_no = request.form.get("Manager_Emp_No")

        if not dept_name or not manager_emp_no:
            return render_template(
                "projects/edit.html",
                project=proj,
                departments=departments,
                employees=employees,
                error="Department and manager are required.",
            )

        start_date = None
        end_date = None
        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            except ValueError:
                return render_template(
                    "projects/edit.html",
                    project=proj,
                    departments=departments,
                    employees=employees,
                    error="Invalid start date.",
                )
        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
            except ValueError:
                return render_template(
                    "projects/edit.html",
                    project=proj,
                    departments=departments,
                    employees=employees,
                    error="Invalid end date.",
                )

        proj.Budget = budget or None
        proj.Date_Started = start_date
        proj.Date_Ended = end_date
        proj.Department_Name = dept_name
        proj.Manager_Emp_No = int(manager_emp_no)

        db.session.commit()
        return redirect(url_for("projects.list_projects"))

    return render_template(
        "projects/edit.html",
        project=proj,
        departments=departments,
        employees=employees,
    )


@bp.route("/<int:project_number>/delete", methods=["POST"])
def delete_project(project_number):
    proj = Project.query.get_or_404(project_number)

    # Delete dependent rows first to avoid FK constraint errors
    Works_On.query.filter_by(Project_Number=project_number).delete()
    TimeEntry.query.filter_by(Project_Number=project_number).delete()
    ProjectMilestone.query.filter_by(Project_Number=project_number).delete()

    db.session.delete(proj)
    db.session.commit()
    return redirect(url_for("projects.list_projects"))

