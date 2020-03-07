
from flask import flash, redirect, render_template, request, url_for, Blueprint
from app import db
from flask_login import login_required, current_user
from app.utils import db_connect
from app.oee.utils import get_planned_output, get_conformance_to_plan, add_update_oee_details, get_hourly_count
from app.models import OEEtbl, Orders, OEEcalc

reports = Blueprint('reports', __name__, template_folder='templates')

