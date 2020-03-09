
from flask import flash, redirect, render_template, request, url_for, Blueprint
from app import db
from flask_login import login_required, current_user
from app.utils import db_connect
from app.oee.utils import get_planned_output, get_conformance_to_plan, add_update_oee_details, get_hourly_count
from app.reports.utils import get_product_count, get_downtime_minutes
from app.models import OEEtbl, Orders, OEEcalc
from datetime import datetime, date, timedelta
from sqlalchemy import desc

reports = Blueprint('reports', __name__, template_folder='templates')

@reports.route("/reports/shift", methods=["GET", "POST"])
@login_required
def shiftreport():

    if request.method == "POST":
        oee_id = request.form.get('shiftSelect')


        if oee_id == None:
            flash('No shift reports available')
            return redirect(url_for('oee.shiftreport'))

        con = db_connect()
        cur = con.cursor()

        # unit count 
        cur.execute("""SELECT SUM(_07+_08+_09+_10+_11+_12+_13+_14) AS amShift,
                                    SUM(_15+_16+_17+_18+_19+_20+_21+_22) AS pmShift FROM 
                                    OEE_details WHERE type = 'Product' AND oee_id = :oee_id  """, {'oee_id':oee_id})
        unit_count = cur.fetchall()
        

        # overall shift details
        cur.execute("""SELECT *, SUM(_07+_08+_09+_10+_11+_12+_13+_14) AS amSum, 
                                    SUM(_15+_16+_17+_18+_19+_20+_21+_22) AS pmSum 
                                    FROM OEE_details WHERE oee_id = :oee_id GROUP BY type
                                    ORDER BY (CASE type WHEN 'Product' THEN 1 END) DESC""", {'oee_id':oee_id})
        oee_stats = cur.fetchall()

        # rejects
        cur.execute(""" SELECT SUM(_07+_08+_09+_10+_11+_12+_13+_14) AS amRejects,
                                    SUM(_15+_16+_17+_18+_19+_20+_21+_22) AS pmRejects FROM 
                                    OEE_details WHERE type = 'Rejects' AND oee_id = :oee_id  """, {'oee_id':oee_id})
        reject_stats = cur.fetchall()

        # downtime stats
        cur.execute("""SELECT *, SUM(_07+_08+_09+_10+_11+_12+_13+_14) AS amShift,
                                    SUM(_15+_16+_17+_18+_19+_20+_21+_22) AS pmShift FROM 
                                    OEE_details WHERE type != 'Product' AND type !='Rejects' AND oee_id = :oee_id  """, {'oee_id':oee_id})
        downtimeStats = cur.fetchall()

        # machine running speed (CPM)
        query = OEEtbl.query.filter(OEEtbl.id==oee_id).first()
        CPM = query.speed

        
        # chart downtime data
        cur.execute("""SELECT type, SUM(_07+_08+_09+_10+_11+_12+_13+_14) AS amSum, 
                                    SUM(_15+_16+_17+_18+_19+_20+_21+_22) AS pmSum 
                                    FROM OEE_details WHERE type != 'Product' AND type !='Rejects' AND oee_id = :oee_id GROUP BY type
                                    """, {'oee_id':oee_id})
        chart_data = cur.fetchall()        


        # calc total lost minutes
        try:
            total_lost_minutes = downtimeStats[0]['amShift'] + downtimeStats[0]['pmShift']
        except TypeError:
            total_lost_minutes = 0
        # calc total units produced
        try:
            total_unit_count = unit_count[0]['amShift'] + unit_count[0]['pmShift']
        except TypeError:
            total_unit_count = 0
        # calc total rejected products
        try:
            total_rejects = reject_stats[0]['amRejects'] + reject_stats[0]['pmRejects']
        except TypeError:
            total_rejects = 0
        # calc good count
        good_count = total_unit_count - total_rejects

        hourly_count = 8

        # add data into object
        data = OEEcalc(hourly_count, total_lost_minutes, CPM, total_unit_count, total_rejects)
        
        # return OEE scores
        availability = round((data.availability()*100),2)
        performance = round((data.performance()*100),2)
        quality = round((data.quality()*100),2)
        oee_score = round((data.OEEscore()*100),2)

        # get conformance To Plan (CTP) score
        ctp = get_conformance_to_plan(oee_id, good_count)

       
        # format lost time
        total_lost_minutes = timedelta(minutes=total_lost_minutes)

        # format shift length
        shift_length = timedelta(minutes=data.shift_length)

        # format good count
        good_count = f'{good_count:,}'

        # format total unit count
        total_unit_count = f'{total_unit_count:,}'

        # calc run time
        run_time = shift_length - total_lost_minutes

        """ Chart Data """
        
        legend = 'Downtime Data (Minutes)'

        labels = []
        for i in chart_data:
            labels.append(i[0])
        
        values = []
        for i in chart_data:
            values.append(i[1] + i[2])
        
        
        
        oee_info = OEEtbl.query.filter_by(id = oee_id).first()

        oee_list = OEEtbl.query.order_by(desc(OEEtbl.start_date)).limit(20).all()

        return render_template('shiftreport.html', good_count=good_count, oee_list=oee_list, oee_stats=oee_stats, 
                                availability=availability, performance=performance, quality=quality, oee_score=oee_score, 
                                total_lost_minutes=total_lost_minutes, total_unit_count=total_unit_count, total_rejects=total_rejects, 
                                shift_length=shift_length, run_time=run_time, legend=legend, labels=labels, values=values, oee_info=oee_info, ctp=ctp)


    oee_list = OEEtbl.query.order_by(desc(OEEtbl.start_date)).limit(20).all()

    return render_template('shiftreport.html', oee_list=oee_list)




@reports.route("/reports/production", methods=["GET", "POST"])
@login_required
def productionReport():

    if request.method == "POST":

        from_date = request.form.get('fromDate')
        to_date = request.form.get('toDate')

        line_num = 'IS NOT NULL'
        
        con = db_connect()
        cur = con.cursor()   

        # get line speed
        cur. execute("""SELECT speed FROM OEE WHERE DATE(start_date) >= '{}' 
                        AND DATE(start_date) <= '{}' AND line_num {} GROUP BY start_date
                        """.format(from_date, to_date, line_num))
        line_speed_result = cur.fetchall()
        line_speed_arr = [i[0] for i in line_speed_result]
        
        day_count = len(get_product_count(from_date, to_date, line_num, 'Product'))
        avg_line_speed = sum(line_speed_arr) / day_count
        daily_count = sum([i[2] + i[3] for i in get_product_count(from_date, to_date, line_num, 'Product')])
        daily_rejects = sum(get_product_count(from_date, to_date, line_num, 'Rejects'))
        daily_downtime = sum([i[1] + i[2] for i in get_downtime_minutes(from_date, to_date, line_num, 'start_date')])

       
        # add data into object
        data = OEEcalc(hourly_count=(day_count*8), total_lost_minutes=daily_downtime, CPM=avg_line_speed, total_unit_count=daily_count, total_rejects=daily_rejects)
        
        # return OEE scores
        availability = round((data.availability()*100),2)
        performance = round((data.performance()*100),2)
        quality = round((data.quality()*100),2)
        oee_score = round((data.OEEscore()*100),2)


        ##################################
        #
        #          Chart Data 
        #
        ##################################
        
        # Downtime Chart (dt)
        dt_legend = 'Downtime Data (Minutes)'

        dt_labels = [i[0] for i in get_downtime_minutes(from_date, to_date, line_num, 'type')]
        dt_values = [i[1] + i[2] for i in get_downtime_minutes(from_date, to_date, line_num, 'type')]

        # Daily production count (dp)
        dp_legend = 'Daily Production Count'

        dp_labels = [i[0] for i in get_product_count(from_date, to_date, line_num, 'Product')]
        dp_values = [i[2] + i[3] for i in get_product_count(from_date, to_date, line_num, 'Product')]
        

        ######################################

        
        data = {
            'from_date': from_date,
            'to_date' : to_date,
            'avg_daily_good_count' : f'{round((daily_count-daily_rejects) / day_count):,}',
            'avg_daily_rejects' : daily_rejects / day_count,
            'avg_daily_downtime' : timedelta(minutes=round(daily_downtime / day_count)),
            'total_count' : f'{daily_count:,}',
            'total_good_count' : f'{daily_count - daily_rejects:,}',
            'total_rejects' : f'{daily_rejects:,}',
            'total_downtime' : timedelta(minutes=round(daily_downtime)),
            'oee_score' : oee_score,
            'availability' : availability,
            'performance' : performance,
            'quality' : quality,
            'dt_legend' : dt_legend,
            'dt_labels' : dt_labels,
            'dt_values' : dt_values,
            'dp_legend' : dp_legend,
            'dp_labels' : dp_labels,
            'dp_values' : dp_values
            
        }


        return render_template('productionreport.html', **data)

    return render_template('productionreport.html')