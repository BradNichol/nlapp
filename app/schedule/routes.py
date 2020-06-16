from flask import flash, redirect, render_template, request, url_for, Blueprint, jsonify
from app import db
from flask_login import login_required
from app.models import Schedule, ScheduleDetails, Product
from app.utils import db_connect
from datetime import datetime, date, timedelta
from sqlalchemy import func, asc, desc

schedule = Blueprint('schedule', __name__, template_folder='templates')


@schedule.route("/schedule")
@login_required
def viewschedule():

    schedule = Schedule.query.order_by(desc(Schedule.wc_date)).limit(60).all()
    
    return render_template('schedule.html', schedule=schedule)

@schedule.route("/schedule/add", methods=["POST"])
@login_required
def addschedule():

    if request.method == "POST":

        # get date
        
        wc_date = datetime.strptime(request.form.get('weekCommencementDate'), '%Y-%m-%d').date()
        format_date = datetime.strftime(wc_date, "%d-%m-%Y")

        # make sure user entered a week commencement date
        today_index = date.weekday(wc_date)
        if today_index != 0:
            flash('Unsuccessful. You can only enter a date starting on a Monday.')
            return redirect(url_for('schedule.viewschedule'))
        
        # stop double entry of same wc date
        check = Schedule.query.filter_by(wc_date=wc_date).first()
        print(check)
        if check:
            flash('Unsuccessful. You have already entered a date for that week.')
            return redirect(url_for('schedule.viewschedule'))
        

        # add into database
        schedule = Schedule(wc_date=wc_date, format_date=format_date)
        db.session.add(schedule)
        db.session.commit()

        return redirect(url_for('schedule.viewschedule'))


@schedule.route("/schedule/<format_date>", methods=["GET", "POST"])
@login_required
def scheduledetails(format_date):
    
    schedule = Schedule.query.filter_by(format_date=format_date).first()


    schedule_details = ScheduleDetails.query.filter_by(schedule_id=schedule.id).order_by(asc(ScheduleDetails.line_num)).all()

    products = Product.query.all()

    return render_template('/scheduledetails.html', schedule=schedule, schedule_details=schedule_details, products=products)


@schedule.route("/schedule/details/add", methods=["GET", "POST"])
@login_required
def addscheduledetails():

    if request.method == "POST":

        schedule_id = request.form.get('schedule_id')
        format_date = request.form.get('format_date')
        product_id = request.form.get('product_id')
        line_num = request.form.get('line_num')
        shift = request.form.get('shift')

        product_check = ScheduleDetails.query.filter_by(schedule_id=schedule_id, product_id=product_id, line_num=line_num).all()

       
        if product_check:
            for i in product_check:
                if i.line_num == int(line_num):
                    flash(f'Product already added to line {line_num}')
                    return redirect(url_for('schedule.scheduledetails', format_date=format_date))


        else:
            addProd = ScheduleDetails(schedule_id=schedule_id, product_id=product_id, shift=shift, line_num=line_num)
            db.session.add(addProd)
            db.session.commit()

            flash('Product added')
            return redirect(url_for('schedule.scheduledetails', format_date=format_date))



@schedule.route("/schedule/details/edit", methods=["GET", "POST"])
@login_required
def editscheduledetails():

    if request.method == "POST":

        schedule_id = request.form.get('schedule_id')
        format_date = request.form.get('format_date')
        product_id = request.form.getlist('product_id')
        line_num = request.form.getlist('line_num')
        #batch_number = request.form.getlist('batch_number')
        monday = request.form.getlist('monday')
        tuesday = request.form.getlist('tuesday')
        wednesday = request.form.getlist('wednesday')
        thursday = request.form.getlist('thursday')
        friday = request.form.getlist('friday')
        saturday = request.form.getlist('saturday')
        sunday = request.form.getlist('sunday')

        con = db_connect()
        cur = con.cursor()

        idcheck = ScheduleDetails.query.filter_by(schedule_id=schedule_id).all()
        
        
        if idcheck:
            for ind, product_id in enumerate(product_id):
                sql = "UPDATE schedule_details SET monday=?, tuesday=?, wednesday=?, thursday=?, friday=?, saturday=?, sunday=? WHERE product_id=? AND schedule_id=? AND line_num=? "
                cur.execute(sql, (monday[ind], tuesday[ind], wednesday[ind], thursday[ind], friday[ind], saturday[ind], sunday[ind], product_id, schedule_id, line_num[ind]))
                con.commit()
            flash('Update successful.')
            return redirect(url_for('schedule.scheduledetails', format_date=format_date))
        

        else:
       
            sql = "INSERT INTO schedule_details (schedule_id, product_id, monday, tuesday, wednesday, thursday, friday, saturday, sunday) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"

            # adding multiple product lines into schedule
            query_args = []
            for ind, product in enumerate(product_id):
                data = (schedule_id, product, monday[ind], tuesday[ind], wednesday[ind], thursday[ind], friday[ind], saturday[ind], sunday[ind])
                query_args.append(data)
            
            
            cur.executemany(sql, query_args)
            con.commit()
            con.close()

        
            flash('Product and values successfully added')
            return redirect(url_for('schedule.viewschedule'))
