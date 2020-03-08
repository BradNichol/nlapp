
from app.utils import db_connect


# Function to convert SQLite result into an array for Product & Reject data
# currently sums AM + PM shifts together
def sql_to_arr(from_date, to_date, line_num, unit_type):
    con = db_connect()
    cur = con.cursor()

    if unit_type == 'Product' or 'Rejects':
        # get daily production count + no. day count 
        cur.execute("""SELECT start_date, type, SUM(_07+_08+_09+_10+_11+_12+_13+_14) AS sum_am_count,
                        SUM(_15+_16+_17+_18+_19+_20+_21+_22) AS sum_pm_count
                        FROM OEE_details JOIN OEE ON OEE_details.oee_id = OEE.id 
                        WHERE DATE(start_date) >= '{}' 
                        AND DATE(start_date) <= '{}' AND line_num {} AND type='{}' GROUP BY start_date  """.format(from_date, to_date, line_num, unit_type ))
        results = cur.fetchall()

        arr = []
        for row in results:        
            arr.append(row[2] + row[3])
        return arr

# Function to convert SQLite result into an array for downtime data
# currently sums AM + PM shifts together
def sql_to_arr2(from_date, to_date, line_num):
    con = db_connect()
    cur = con.cursor()
    cur.execute("""SELECT SUM(_07+_08+_09+_10+_11+_12+_13+_14) AS sum_downtime_am,
                    SUM(_15+_16+_17+_18+_19+_20+_21+_22) sum_downtime_pm 
                    FROM OEE_details JOIN OEE ON OEE_details.oee_id = OEE.id 
                    WHERE type != 'Product' AND type !='Rejects' 
                    AND DATE(start_date) >= '{}' 
                    AND DATE(start_date) <= '{}' AND line_num {} GROUP BY start_date """.format(from_date, to_date, line_num))
    results = cur.fetchall()
    
    arr = []
    for row in results:        
        arr.append(row[0] + row[1])
    return arr

