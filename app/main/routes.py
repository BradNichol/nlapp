from app import app, db
from flask import flash, redirect, render_template, request, session, url_for, Blueprint
import sqlite3 as sqlite
from app.models import User, Schedule
from flask_login import current_user, login_required
from app.utils import db_connect
from datetime import datetime, date, timedelta


main = Blueprint('main', __name__)

@main.route("/")
@login_required
def index():

    con = db_connect()
    cur = con.cursor()
    
    cur.execute("SELECT COUNT(cname) FROM customers")
    result1 = cur.fetchone()[0]
    cur.execute("SELECT COUNT(id) FROM recipes GROUP BY rname")
    result3 = cur.fetchone()[0]

    # Daily units produced chart
    todayIndex = date.weekday(date.today())

    todaysDate = date.today()

    if todayIndex == 0:
        firstDateOfWeek = todaysDate
    elif todayIndex == 1:
        firstDateOfWeek = todaysDate - timedelta(days=1)
    elif todayIndex == 2:
        firstDateOfWeek = todaysDate - timedelta(days=2)
    elif todayIndex == 3:
        firstDateOfWeek = todaysDate - timedelta(days=3)
    elif todayIndex == 4:
        firstDateOfWeek = todaysDate - timedelta(days=4)
    elif todayIndex == 5:
        firstDateOfWeek = todaysDate - timedelta(days=5)
    else:
        firstDateOfWeek = todaysDate - timedelta(days=6)
    
    # get schedule id for displaying number of units required in a week 
    schedule_id = Schedule.query.filter_by(wc_date = firstDateOfWeek).first()
    
    # exception added in case user doesn't add schedule
    try:
        cur.execute("""SELECT SUM(monday + tuesday + wednesday + thursday + friday + saturday + sunday) as weeklyUnitsRequired 
                    from schedule_details WHERE schedule_id = :schedule_id""", {'schedule_id':schedule_id.id})
        weeklyUnitsRequired = cur.fetchone()
        weeklyUnitsRequired = f'{weeklyUnitsRequired["weeklyUnitsRequired"]:,}'
    except:
        weeklyUnitsRequired = 'N/A'

    
    
    


    
    # unit count 
    cur.execute("""SELECT start_date, SUM(_07+_08+_09+_10+_11+_12+_13+_14+_15+_16+_17+_18+_19+_20+_21+_22) AS totalUnits FROM 
                                OEE_details JOIN OEE ON OEE_details.oee_id = OEE.id WHERE type = 'Product' 
                                AND DATE(start_date) >= '{}' AND DATE(start_date) <= '{}' GROUP BY start_date  """.format(firstDateOfWeek, todaysDate))
    totalWeeklyUnits = cur.fetchall()

    # Chart Data 
    
    legend = 'Total Units Produced By Day'

    labels = []
    for i in totalWeeklyUnits:
        day = datetime.strptime(i[0], '%Y-%m-%d')
        labels.append(day.strftime('%A'))
    
    values = []
    for i in totalWeeklyUnits:
        values.append(i[1])
    

    return render_template('index.html', result1=result1, weeklyUnitsRequired=weeklyUnitsRequired, totalUnitsProduced=totalUnitsProduced, result3=result3, legend=legend, labels=labels, values=values)

    




