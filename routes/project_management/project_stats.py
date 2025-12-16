from flask import Blueprint, render_template
from sqlalchemy import func
from models import db, Project, Employee, Works_On, TimeEntry, ProjectMilestone

bp = Blueprint("project_stats", __name__, url_prefix="/projects")

@bp.route("/<int:project_number>/stats")
def stats(project_number):
    project = Project.query.get_or_404(project_number)

    # Team count (Works_On)
    team_count = (
        db.session.query(func.count(Works_On.Employee_No))
        .filter(Works_On.Project_Number == project_number)
        .scalar()
    ) or 0

    # Total person-hours from TimeEntry (better than Works_On.Time_Spent for “hours” stats)
    total_hours = (
        db.session.query(func.coalesce(func.sum(TimeEntry.Hours), 0))
        .filter(TimeEntry.Project_Number == project_number)
        .scalar()
    )

    # Milestone counts
    total_milestones = (
        db.session.query(func.count(ProjectMilestone.Milestone_ID))
        .filter(ProjectMilestone.Project_Number == project_number)
        .scalar()
    ) or 0

    completed_milestones = (
        db.session.query(func.count(ProjectMilestone.Milestone_ID))
        .filter(ProjectMilestone.Project_Number == project_number)
        .filter(ProjectMilestone.Status == "Completed")
        .scalar()
    ) or 0

    remaining_milestones = total_milestones - completed_milestones

    return render_template(
        "projects/stats.html",
        project=project,
        team_count=team_count,
        total_hours=total_hours,
        total_milestones=total_milestones,
        completed_milestones=completed_milestones,
        remaining_milestones=remaining_milestones,
    )
