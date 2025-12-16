from flask import Blueprint, render_template, request, redirect, url_for
from datetime import datetime
from models import db, Project, ProjectMilestone

bp = Blueprint("milestones", __name__, url_prefix="/projects")

STATUSES = ["Not Started", "In Progress", "Completed"]

@bp.route("/<int:project_number>/milestones")
def list_milestones(project_number):
    project = Project.query.get_or_404(project_number)
    milestones = (
        ProjectMilestone.query
        .filter(ProjectMilestone.Project_Number == project_number)
        .order_by(ProjectMilestone.Due_Date.is_(None), ProjectMilestone.Due_Date)
        .all()
    )
    return render_template("milestones/list.html", project=project, milestones=milestones)


@bp.route("/<int:project_number>/milestones/create", methods=["GET", "POST"])
def create_milestone(project_number):
    project = Project.query.get_or_404(project_number)

    if request.method == "POST":
        title = request.form.get("Title", "").strip()
        desc = request.form.get("Description", "").strip()
        status = request.form.get("Status", "Not Started")
        due_str = request.form.get("Due_Date", "").strip()
        completed_str = request.form.get("Completed_Date", "").strip()

        if not title:
            return render_template(
                "milestones/create.html",
                project=project,
                statuses=STATUSES,
                error="Title is required.",
            )

        due_date = None
        if due_str:
            due_date = datetime.strptime(due_str, "%Y-%m-%d").date()

        completed_date = None
        if completed_str:
            completed_date = datetime.strptime(completed_str, "%Y-%m-%d").date()

        m = ProjectMilestone(
            Project_Number=project_number,
            Title=title,
            Description=desc or None,
            Status=status,
            Due_Date=due_date,
            Completed_Date=completed_date,
        )
        db.session.add(m)
        db.session.commit()
        return redirect(url_for("milestones.list_milestones", project_number=project_number))

    return render_template("milestones/create.html", project=project, statuses=STATUSES)


@bp.route("/<int:project_number>/milestones/<int:milestone_id>/edit", methods=["GET", "POST"])
def edit_milestone(project_number, milestone_id):
    project = Project.query.get_or_404(project_number)
    m = ProjectMilestone.query.get_or_404(milestone_id)

    if request.method == "POST":
        title = request.form.get("Title", "").strip()
        desc = request.form.get("Description", "").strip()
        status = request.form.get("Status", "Not Started")
        due_str = request.form.get("Due_Date", "").strip()
        completed_str = request.form.get("Completed_Date", "").strip()

        if not title:
            return render_template(
                "milestones/edit.html",
                project=project,
                milestone=m,
                statuses=STATUSES,
                error="Title is required.",
            )

        m.Title = title
        m.Description = desc or None
        m.Status = status

        m.Due_Date = datetime.strptime(due_str, "%Y-%m-%d").date() if due_str else None
        m.Completed_Date = datetime.strptime(completed_str, "%Y-%m-%d").date() if completed_str else None

        db.session.commit()
        return redirect(url_for("milestones.list_milestones", project_number=project_number))

    return render_template("milestones/edit.html", project=project, milestone=m, statuses=STATUSES)


@bp.route("/<int:project_number>/milestones/<int:milestone_id>/delete", methods=["POST"])
def delete_milestone(project_number, milestone_id):
    m = ProjectMilestone.query.get_or_404(milestone_id)
    db.session.delete(m)
    db.session.commit()
    return redirect(url_for("milestones.list_milestones", project_number=project_number))
