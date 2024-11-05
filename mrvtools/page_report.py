import frappe
# import pandas as pd
from frappe.utils import get_fullname
from datetime import date, timedelta ,datetime
import statistics
 
 
def dates_bwn_twodates(start_dt = None,end_dt=None):
	start_date = datetime.strptime(start_dt, "%Y-%m-%d")
	end_date = datetime.strptime(end_dt, "%Y-%m-%d")
	delta = timedelta(days=1)
	dates = []
	while start_date.date() <= end_date.date():
		dates.append(datetime.date(start_date))
		start_date += delta
	# frappe.log_error(title="---dates", message = dates)
	return dates

def get_total_adaptation_report():
	adaptation_report = {
		"User": {
			"fields": ["tot_sales"],
			"method": "mrvtools.page_report.get_total_adaptation_report_data",
			"company_disabled": 1,
			"icon": "users",
		}
	}
	return adaptation_report


def get_time_list(date):
	return ["12 AM","1 AM","2 AM","3 AM","4 AM","5 AM","6 AM","7 AM","8 AM","9 AM","10 AM","11 AM",
		 	"12 PM","1 PM","2 PM","3 PM","4 PM","5 PM","6 PM","7 PM","8 PM","9 PM","10 PM","11 PM"]

def get_formated_time(time):
	info = {0:"12 AM",1:"1 AM",2:"2 AM",3:"3 AM",4:"4 AM",5:"5 AM",6:"6 AM",7:"7 AM",
		 	8:"8 AM",9:"9 AM",10:"10 AM",11:"11 AM",12:"12 PM",13:"1 PM",14:"2 PM",
			15:"3 PM",16:"4 PM",17:"5 PM",18:"6 PM",19:"7 PM",20:"8 PM",21:"9 PM",
			22:"10 PM",23:"11 PM"}
	return info[time]



