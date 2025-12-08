# models.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Division(db.Model):
    __tablename__ = "Division"

    Division_Name = db.Column(db.String(100), primary_key=True)
    Head_Emp_No = db.Column(
        db.Integer,
        db.ForeignKey("Employee.Employee_No"),
        nullable=True
    )


class Department(db.Model):
    __tablename__ = "Department"

    Department_Name = db.Column(db.String(100), primary_key=True)
    Budget = db.Column(db.Numeric(12, 2))
    Division_Name = db.Column(
        db.String(100),
        db.ForeignKey("Division.Division_Name"),
        nullable=False
    )
    Head_Emp_No = db.Column(
        db.Integer,
        db.ForeignKey("Employee.Employee_No"),
        nullable=True
    )


class Building(db.Model):
    __tablename__ = "Building"

    Building_Code = db.Column(db.String(20), primary_key=True)
    Name = db.Column(db.String(100))
    Year_Bought = db.Column(db.Integer)
    Cost = db.Column(db.Numeric(14, 2))


class Employee_Title(db.Model):
    __tablename__ = "Employee_Title"

    Title = db.Column(db.String(100), primary_key=True)
    Salary = db.Column(db.Numeric(12, 2))


class Employee(db.Model):
    __tablename__ = "Employee"

    Employee_No = db.Column(db.Integer, primary_key=True)
    Employee_Name = db.Column(db.String(100))
    Phone_Number = db.Column(db.String(20))
    Starting_Date = db.Column(db.Date)
    Title = db.Column(
        db.String(100),
        db.ForeignKey("Employee_Title.Title")
    )
    Department_Name = db.Column(
        db.String(100),
        db.ForeignKey("Department.Department_Name"),
        nullable=True
    )
    Division_Name = db.Column(
        db.String(100),
        db.ForeignKey("Division.Division_Name"),
        nullable=True
    )


class Project(db.Model):
    __tablename__ = "Project"

    Project_Number = db.Column(db.Integer, primary_key=True)
    Budget = db.Column(db.Numeric(12, 2))
    Date_Started = db.Column(db.Date)
    Date_Ended = db.Column(db.Date)
    Department_Name = db.Column(
        db.String(100),
        db.ForeignKey("Department.Department_Name"),
        nullable=False
    )
    Manager_Emp_No = db.Column(
        db.Integer,
        db.ForeignKey("Employee.Employee_No"),
        nullable=False
    )


class Room(db.Model):
    __tablename__ = "Room"

    Room_Number = db.Column(db.String(20), primary_key=True)
    Square_Feet = db.Column(db.Integer)
    Type = db.Column(db.String(50))
    Building_Code = db.Column(
        db.String(20),
        db.ForeignKey("Building.Building_Code"),
        nullable=False
    )
    Department_Name = db.Column(
        db.String(100),
        db.ForeignKey("Department.Department_Name"),
        nullable=False
    )


class Works_On(db.Model):
    __tablename__ = "Works_On"

    Employee_No = db.Column(
        db.Integer,
        db.ForeignKey("Employee.Employee_No"),
        primary_key=True
    )
    Project_Number = db.Column(
        db.Integer,
        db.ForeignKey("Project.Project_Number"),
        primary_key=True
    )
    Time_Spent = db.Column(db.Numeric(10, 2))
    Role = db.Column(db.String(100))
