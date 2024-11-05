# Copyright (c) 2023, tridotstech and contributors
# For license information, please see license.txt

import frappe , json
from frappe.model.document import Document
from frappe.utils.password import update_password
from frappe.utils.password import get_decrypted_password

class UserRegistration(Document):
	def on_submit(self):
		self.create_approved_user()
		# self.check_user_exists(self.ghg,self.reports,self.project_tracking)

	def on_update_after_submit(self):
		self.create_approved_user()
		# self.check_user_exists(self.ghg,self.reports,self.project_tracking)
	


	def create_approved_user(self):
		if not frappe.db.exists("Approved User",{"email":self.email_id}):

			doc = frappe.new_doc("Approved User")

			doc.first_name = self.user_name
			doc.mobile_no = self.contact_number
			doc.email = self.email_id
			doc.role = self.role
			ghgData = self.ghg
			for i in ghgData:
				row = doc.append('ghg',{})
				row.project_tracking = i.project_tracking

			projectTrackingData = self.project_tracking
			for i in projectTrackingData:
				row = doc.append('project_tracking',{})
				row.project_tracking = i.project_tracking

			reportsData = self.reports
			for i in reportsData:
				row = doc.append('reports',{})
				row.project_tracking = i.project_tracking

			
			doc.insert(ignore_permissions = True)
			return({"message":"User Registration Successful! Waiting for Approval.","data":[ghgData,projectTrackingData,reportsData]})
		else:
			doc = frappe.get_doc("Approved User",self.email_id)
			ghgData = self.ghg
			doc.ghg = []
			doc.project_tracking = []
			doc.reports = []
			for i in ghgData:
				row = doc.append('ghg',{})
				row.project_tracking = i.project_tracking

			projectTrackingData = self.project_tracking
			for i in projectTrackingData:
				row = doc.append('project_tracking',{})
				row.project_tracking = i.project_tracking

			reportsData = self.reports
			for i in reportsData:
				row = doc.append('reports',{})
				row.project_tracking = i.project_tracking
			doc.save(ignore_permissions = True)
			frappe.db.commit()
	


@frappe.whitelist(allow_guest = True)
def createUser(formData):
	formData = json.loads(formData)
	if not frappe.db.exists("User Registration",{"email_id":formData['email_id']}):

		doc = frappe.new_doc("User Registration")

		doc.user_name = formData['user_name']
		doc.contact_number = formData['contact_number']
		doc.email_id = formData['email_id']
		# doc.password = formData['password']
		# doc.confirm_password = formData['confirm_password']
		doc.role = formData['role']

		ghgData = formData['GHG']
		for i in ghgData:
			row = doc.append('ghg',{})
			row.project_tracking = i

		projectTrackingData = formData['Project Tracking']
		for i in projectTrackingData:
			row = doc.append('project_tracking',{})
			row.project_tracking = i

		# projectTrackingString = ",".join(projectTrackingData)
		# doc.project_tracking = projectTrackingString

		reportsData = formData['Reports']
		for i in reportsData:
			row = doc.append('reports',{})
			row.project_tracking = i
		# reportsString = ",".join(reportsData)
		# doc.reports = reportsString

		
		doc.insert(ignore_permissions = True)
		return({"message":"User Registration Successful! Waiting for Approval.","data":[ghgData,projectTrackingData,reportsData]})
	else:
		frappe.throw("Email Id Already Registred")

@frappe.whitelist(allow_guest = True)
def insert_approved_users():
	users = frappe.db.get_all("User Registration",fields=["*"])
	for user in users:
		frappe.log_error(f"{user.email_id}",user)
		if user.workflow_state == "Approved":
			if not frappe.db.exists("Approved User",{"email":user.email_id}):

				doc = frappe.new_doc("Approved User")
				doc.first_name = user.user_name
				doc.mobile_no = user.contact_number
				doc.email = user.email_id
				doc.role = user.role
				
				if user.ghg:
					ghgData = user.ghg
					for i in ghgData:
						row = doc.append('ghg',{})
						row.project_tracking = i.project_tracking
				if user.project_tracking:
					projectTrackingData = user.project_tracking
					for i in projectTrackingData:
						row = doc.append('project_tracking',{})
						row.project_tracking = i.project_tracking
				if user.reports:
					reportsData = user.reports
					for i in reportsData:
						row = doc.append('reports',{})
						row.project_tracking = i.project_tracking
				doc.insert(ignore_permissions = True)
				frappe.db.commit()
	return({"status":"Success"})