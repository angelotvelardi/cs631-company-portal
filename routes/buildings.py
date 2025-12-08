# routes/buildings.py
from flask import Blueprint, render_template, request, redirect, url_for
from models import db, Building

bp = Blueprint("buildings", __name__, url_prefix="/buildings")


@bp.route("/")
def list_buildings():
    buildings = Building.query.order_by(Building.Building_Code).all()
    return render_template("buildings/list.html", buildings=buildings)


@bp.route("/create", methods=["GET", "POST"])
def create_building():
    if request.method == "POST":
        code = request.form.get("Building_Code", "").strip()
        name = request.form.get("Name", "").strip()
        year = request.form.get("Year_Bought", "").strip()
        cost = request.form.get("Cost", "").strip()

        if not code:
            return render_template(
                "buildings/create.html",
                error="Building code is required.",
            )

        existing = Building.query.get(code)
        if existing:
            return render_template(
                "buildings/create.html",
                error="Building with that code already exists.",
            )

        b = Building(
            Building_Code=code,
            Name=name or None,
            Year_Bought=int(year) if year else None,
            Cost=cost or None,
        )
        db.session.add(b)
        db.session.commit()
        return redirect(url_for("buildings.list_buildings"))

    return render_template("buildings/create.html")


@bp.route("/<building_code>/edit", methods=["GET", "POST"])
def edit_building(building_code):
    b = Building.query.get_or_404(building_code)

    if request.method == "POST":
        name = request.form.get("Name", "").strip()
        year = request.form.get("Year_Bought", "").strip()
        cost = request.form.get("Cost", "").strip()

        b.Name = name or None
        b.Year_Bought = int(year) if year else None
        b.Cost = cost or None

        db.session.commit()
        return redirect(url_for("buildings.list_buildings"))

    return render_template("buildings/edit.html", building=b)


@bp.route("/<building_code>/delete", methods=["POST"])
def delete_building(building_code):
    b = Building.query.get_or_404(building_code)
    db.session.delete(b)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
    return redirect(url_for("buildings.list_buildings"))
