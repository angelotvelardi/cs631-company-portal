# routes/rooms.py
from flask import Blueprint, render_template, request, redirect, url_for
from models import db, Room, Building, Department

bp = Blueprint("rooms", __name__, url_prefix="/rooms")


@bp.route("/")
def list_rooms():
    rooms = (
        db.session.query(Room, Building, Department)
        .join(Building, Room.Building_Code == Building.Building_Code)
        .join(Department, Room.Department_Name == Department.Department_Name)
        .order_by(Room.Room_Number)
        .all()
    )
    return render_template("rooms/list.html", rooms=rooms)


@bp.route("/create", methods=["GET", "POST"])
def create_room():
    buildings = Building.query.order_by(Building.Building_Code).all()
    departments = Department.query.order_by(Department.Department_Name).all()

    if request.method == "POST":
        number = request.form.get("Room_Number", "").strip()
        sq = request.form.get("Square_Feet", "").strip()
        rtype = request.form.get("Type", "").strip()
        building_code = request.form.get("Building_Code")
        dept_name = request.form.get("Department_Name")

        if not number or not building_code or not dept_name:
            return render_template(
                "rooms/create.html",
                buildings=buildings,
                departments=departments,
                error="Room number, building, and department are required.",
            )

        existing = Room.query.get(number)
        if existing:
            return render_template(
                "rooms/create.html",
                buildings=buildings,
                departments=departments,
                error="Room with that number already exists.",
            )

        room = Room(
            Room_Number=number,
            Square_Feet=int(sq) if sq else None,
            Type=rtype or None,
            Building_Code=building_code,
            Department_Name=dept_name,
        )
        db.session.add(room)
        db.session.commit()
        return redirect(url_for("rooms.list_rooms"))

    return render_template("rooms/create.html", buildings=buildings, departments=departments)


@bp.route("/<room_number>/edit", methods=["GET", "POST"])
def edit_room(room_number):
    room = Room.query.get_or_404(room_number)
    buildings = Building.query.order_by(Building.Building_Code).all()
    departments = Department.query.order_by(Department.Department_Name).all()

    if request.method == "POST":
        sq = request.form.get("Square_Feet", "").strip()
        rtype = request.form.get("Type", "").strip()
        building_code = request.form.get("Building_Code")
        dept_name = request.form.get("Department_Name")

        if not building_code or not dept_name:
            return render_template(
                "rooms/edit.html",
                room=room,
                buildings=buildings,
                departments=departments,
                error="Building and department are required.",
            )

        room.Square_Feet = int(sq) if sq else None
        room.Type = rtype or None
        room.Building_Code = building_code
        room.Department_Name = dept_name

        db.session.commit()
        return redirect(url_for("rooms.list_rooms"))

    return render_template(
        "rooms/edit.html",
        room=room,
        buildings=buildings,
        departments=departments,
    )


@bp.route("/<room_number>/delete", methods=["POST"])
def delete_room(room_number):
    room = Room.query.get_or_404(room_number)
    db.session.delete(room)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
    return redirect(url_for("rooms.list_rooms"))
