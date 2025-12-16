# app.py
import os
from flask import Flask, render_template
from models import db
from routes.divisions import bp as divisions_bp
from routes.departments import bp as departments_bp
from routes.buildings import bp as buildings_bp
from routes.rooms import bp as rooms_bp
from routes.employees import bp as employees_bp
from routes.projects import bp as projects_bp
from routes.workson import bp as workson_bp
from routes.titles import bp as titles_bp
from routes.hr.project_employees import bp as project_employees_bp
from routes.hr.time_entries import bp as time_entries_bp
from routes.hr.payroll import bp as payroll_bp
from routes.project_management.project_stats import bp as project_stats_bp
from routes.project_management.milestones import bp as milestones_bp



def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key")


    db.init_app(app)

    # Register blueprints
    app.register_blueprint(divisions_bp)
    app.register_blueprint(departments_bp)
    app.register_blueprint(buildings_bp)
    app.register_blueprint(rooms_bp)
    app.register_blueprint(employees_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(workson_bp)
    app.register_blueprint(titles_bp)
    app.register_blueprint(project_employees_bp)
    app.register_blueprint(time_entries_bp)
    app.register_blueprint(payroll_bp)
    app.register_blueprint(project_stats_bp)
    app.register_blueprint(milestones_bp)


    @app.route("/")
    def home():
        return render_template("home.html")

    with app.app_context():
        db.create_all()

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)

