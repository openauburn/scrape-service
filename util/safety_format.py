from datetime import datetime

err_dt = "%Y-%m-%d %H:%M:%S" 

def string_format(string, r):
    if string == " " or string == "NA":
        return None
    else:
        return string.strip()

def date_format(mm_dd_yyyy, r):
    try:
        date = datetime.strptime(mm_dd_yyyy, "%m/%d/%Y")
        return datetime.strftime(date, "%Y-%m-%d")
    except Exception as err:
        r.errors.append({
            "message": f"Failure while processing date {mm_dd_yyyy}",
            "message_ext": str(err), 
            "occurred_at": datetime.strftime(datetime.now(), err_dt)
        })
        return "1970-01-01"
        
def time_format(hh_mm, r):
    try:
        time = datetime.strptime(hh_mm, "%H:%M")
        return datetime.strftime(time, "%H:%M")
    except Exception as err:
        r.errors.append({"message": f"Failure while processing time {hh_mm}",
            "message_ext": str(err), 
            "occurred_at": datetime.strftime(datetime.now(), err_dt)})
        return "00:00"

def datetime_format(date, time, r):
    new_date = date_format(date, r)
    new_time = time_format(time, r)
    return new_date + " " + new_time