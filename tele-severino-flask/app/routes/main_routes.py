from flask import Blueprint, render_template, request, redirect, url_for
from app.repositories.category_repository import list_categories
from app.services.specialist_service import get_home_specialists

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def root():
    return redirect(url_for("main.splash", next="/login"))


@main_bp.route("/inicio")
def splash():
    next_url = request.args.get("next", "/login")
    return render_template("splash.html", next_url=next_url)


@main_bp.route("/home")
def home():
    categories = list_categories()
    specialists = get_home_specialists()
    return render_template("home.html", categories=categories, specialists=specialists)
