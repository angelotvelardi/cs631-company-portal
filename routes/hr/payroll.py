from flask import Blueprint, render_template, request, redirect, url_for
from sqlalchemy import func
from datetime import date
from decimal import Decimal
from models import db, PayrollHistory, Employee, Employee_Title, ProjectEmployee, TimeEntry

bp = Blueprint("payroll", __name__, url_prefix="/payroll")

FED = Decimal("0.10")
STATE = Decimal("0.05")
OTHER = Decimal("0.03")


@bp.route("/")
def payroll_home():
    return render_template("payroll/home.html")


@bp.route("/run", methods=["GET", "POST"])
def run_payroll():
    if request.method == "POST":
        year_str = request.form.get("Pay_Year", "").strip()
        month_str = request.form.get("Pay_Month", "").strip()

        if not year_str or not month_str:
            return render_template("payroll/run.html", error="Year and month are required.")

        year = int(year_str)
        month = int(month_str)

        # Determine month date range
        start = date(year, month, 1)
        if month == 12:
            end = date(year + 1, 1, 1)
        else:
            end = date(year, month + 1, 1)

        # --- Salaried employees: use Employee_Title.Salary ---
        salaried_rows = (
            db.session.query(Employee, Employee_Title)
            .join(Employee_Title, Employee.Title == Employee_Title.Title)
            .all()
        )

        created = 0

        for emp, title in salaried_rows:
            # Skip if employee is also an hourly project-employee
            # (You can remove this if you want to allow both)
            if ProjectEmployee.query.get(emp.Employee_No):
                continue

            exists = (
                PayrollHistory.query.filter_by(Employee_No=emp.Employee_No, Pay_Year=year, Pay_Month=month)
                .first()
            )
            if exists:
                continue

            gross = Decimal(str(title.Salary))
            federal = (gross * FED).quantize(Decimal("0.01"))
            state = (gross * STATE).quantize(Decimal("0.01"))
            other = (gross * OTHER).quantize(Decimal("0.01"))
            net = (gross - federal - state - other).quantize(Decimal("0.01"))

            ph = PayrollHistory(
                Employee_No=emp.Employee_No,
                Pay_Year=year,
                Pay_Month=month,
                Gross_Pay=gross,
                Federal_Tax=federal,
                State_Tax=state,
                Other_Tax=other,
                Net_Pay=net,
                Rate_Type="SALARY",
                Base_Rate_Used=title.Salary,
            )
            db.session.add(ph)
            created += 1

        # --- Hourly employees: hours for month * hourly_rate ---
        hourly_rows = ProjectEmployee.query.all()

        for pe in hourly_rows:
            exists = (
                PayrollHistory.query.filter_by(Employee_No=pe.Employee_No, Pay_Year=year, Pay_Month=month)
                .first()
            )
            if exists:
                continue

            total_hours = (
                db.session.query(func.coalesce(func.sum(TimeEntry.Hours), 0))
                .filter(TimeEntry.Employee_No == pe.Employee_No)
                .filter(TimeEntry.Work_Date >= start)
                .filter(TimeEntry.Work_Date < end)
                .scalar()
            )

            rate = Decimal(str(pe.Hourly_Rate))
            gross = (Decimal(str(total_hours)) * rate).quantize(Decimal("0.01"))

            federal = (gross * FED).quantize(Decimal("0.01"))
            state = (gross * STATE).quantize(Decimal("0.01"))
            other = (gross * OTHER).quantize(Decimal("0.01"))
            net = (gross - federal - state - other).quantize(Decimal("0.01"))

            ph = PayrollHistory(
                Employee_No=pe.Employee_No,
                Pay_Year=year,
                Pay_Month=month,
                Gross_Pay=gross,
                Federal_Tax=federal,
                State_Tax=state,
                Other_Tax=other,
                Net_Pay=net,
                Rate_Type="HOURLY",
                Base_Rate_Used=pe.Hourly_Rate,
            )
            db.session.add(ph)
            created += 1

        db.session.commit()
        return redirect(url_for("payroll.history", year=year, month=month))

    return render_template("payroll/run.html")


@bp.route("/history")
def history():
    year = request.args.get("year", type=int)
    month = request.args.get("month", type=int)

    q = (
        db.session.query(PayrollHistory, Employee)
        .join(Employee, PayrollHistory.Employee_No == Employee.Employee_No)
        .order_by(PayrollHistory.Pay_Year.desc(), PayrollHistory.Pay_Month.desc(), Employee.Employee_Name)
    )

    if year and month:
        q = q.filter(PayrollHistory.Pay_Year == year, PayrollHistory.Pay_Month == month)

    rows = q.all()
    return render_template("payroll/history.html", rows=rows, year=year, month=month)
