# routes/employees.py
from flask import Blueprint, render_template, request, redirect, url_for
from models import db, Employee, Employee_Title, Department, Division
from datetime import datetime

bp = Blueprint("employees", __name__, url_prefix="/employees")


@bp.route("/")
def list_employees():
    employees = (
        db.session.query(Employee, Department, Division, Employee_Title)
        .outerjoin(Department, Employee.Department_Name == Department.Department_Name)
        .outerjoin(Division, Employee.Division_Name == Division.Division_Name)
        .outerjoin(Employee_Title, Employee.Title == Employee_Title.Title)
        .order_by(Employee.Employee_Name)
        .all()
    )
    return render_template("employees/list.html", employees=employees)


@bp.route("/create", methods=["GET", "POST"])
def create_employee():
    departments = Department.query.order_by(Department.Department_Name).all()
    divisions = Division.query.order_by(Division.Division_Name).all()
    titles = Employee_Title.query.order_by(Employee_Title.Title).all()

    if request.method == "POST":
        emp_no_str = request.form.get("Employee_No", "").strip()
        name = request.form.get("Employee_Name", "").strip()
        phone = request.form.get("Phone_Number", "").strip()
        start_date_str = request.form.get("Starting_Date", "").strip()
        title = request.form.get("Title") or None
        dept_name = request.form.get("Department_Name") or None
        div_name = request.form.get("Division_Name") or None

        if not emp_no_str or not name:
            return render_template(
                "employees/create.html",
                departments=departments,
                divisions=divisions,
                titles=titles,
                error="Employee number and name are required.",
            )

        try:
            emp_no = int(emp_no_str)
        except ValueError:
            return render_template(
                "employees/create.html",
                departments=departments,
                divisions=divisions,
                titles=titles,
                error="Employee number must be an integer.",
            )

        if Employee.query.get(emp_no):
            return render_template(
                "employees/create.html",
                departments=departments,
                divisions=divisions,
                titles=titles,
                error="An employee with that number already exists.",
            )

        start_date = None
        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            except ValueError:
                return render_template(
                    "employees/create.html",
                    departments=departments,
                    divisions=divisions,
                    titles=titles,
                    error="Invalid starting date format.",
                )

        emp = Employee(
            Employee_No=emp_no,
            Employee_Name=name,
            Phone_Number=phone or None,
            Starting_Date=start_date,
            Title=title,
            Department_Name=dept_name,
            Division_Name=div_name,
        )
        db.session.add(emp)
        db.session.commit()
        return redirect(url_for("employees.list_employees"))

    return render_template(
        "employees/create.html",
        departments=departments,
        divisions=divisions,
        titles=titles,
    )


@bp.route("/<int:employee_no>/edit", methods=["GET", "POST"])
def edit_employee(employee_no):
    emp = Employee.query.get_or_404(employee_no)
    departments = Department.query.order_by(Department.Department_Name).all()
    divisions = Division.query.order_by(Division.Division_Name).all()
    titles = Employee_Title.query.order_by(Employee_Title.Title).all()

    if request.method == "POST":
        name = request.form.get("Employee_Name", "").strip()
        phone = request.form.get("Phone_Number", "").strip()
        start_date_str = request.form.get("Starting_Date", "").strip()
        title = request.form.get("Title") or None
        dept_name = request.form.get("Department_Name") or None
        div_name = request.form.get("Division_Name") or None

        if not name:
            return render_template(
                "employees/edit.html",
                employee=emp,
                departments=departments,
                divisions=divisions,
                titles=titles,
                error="Employee name is required.",
            )

        start_date = None
        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            except ValueError:
                return render_template(
                    "employees/edit.html",
                    employee=emp,
                    departments=departments,
                    divisions=divisions,
                    titles=titles,
                    error="Invalid starting date format.",
                )

        emp.Employee_Name = name
        emp.Phone_Number = phone or None
        emp.Starting_Date = start_date
        emp.Title = title
        emp.Department_Name = dept_name
        emp.Division_Name = div_name

        db.session.commit()
        return redirect(url_for("employees.list_employees"))

    return render_template(
        "employees/edit.html",
        employee=emp,
        departments=departments,
        divisions=divisions,
        titles=titles,
    )


@bp.route("/<int:employee_no>/delete", methods=["POST"])
def delete_employee(employee_no):
    emp = Employee.query.get_or_404(employee_no)
    db.session.delete(emp)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        # optional: flash an error if there are FK constraints
    return redirect(url_for("employees.list_employees"))
