# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE
from datetime import timedelta

import frappe
import frappe.defaults
import frappe.permissions
import frappe.share
from frappe import STANDARD_USERS, _, msgprint, throw
from frappe.core.doctype.user_type.user_type import user_linked_with_permission_on_doctype
from frappe.desk.doctype.notification_settings.notification_settings import (
	create_notification_settings,
	toggle_notifications,
)
from frappe.desk.notifications import clear_notifications
from frappe.model.document import Document
from frappe.query_builder import DocType
from frappe.rate_limiter import rate_limit
from frappe.utils.password import update_password
from frappe.utils.password import get_decrypted_password
from frappe.utils import (
	cint,
	escape_html,
	flt,
	format_datetime,
	get_formatted_email,
	get_system_timezone,
	has_gravatar,
	now_datetime,
	today,
)
from frappe.utils.deprecations import deprecated
from frappe.utils.password import check_password, get_password_reset_limit
from frappe.utils.user import get_system_managers
from frappe.website.utils import is_signup_disabled


class ApprovedUser(Document):

	def autoname(self):
		"""set name as Email Address"""
		if self.get("is_admin") or self.get("is_guest"):
			self.name = self.first_name
		else:
			self.email = self.email.strip().lower()
			self.name = self.email

	def onload(self):
		from frappe.config import get_modules_from_all_apps

		self.set_onload("all_modules", sorted(m.get("module_name") for m in get_modules_from_all_apps()))

	def before_insert(self):
		self.flags.in_insert = True

	def after_insert(self):
		create_notification_settings(self.name)
		frappe.cache().delete_key("users_for_mentions")
		frappe.cache().delete_key("enabled_users")

	def password_reset_mail(self, link):
		self.send_login_mail(_("Password Reset"), "password_reset", {"link": link}, now=True)

	def send_login_mail(self, subject, template, add_args, now=None):
		"""send mail with login details"""
		from frappe.utils import get_url
		from frappe.utils.user import get_user_fullname

		created_by = get_user_fullname(frappe.session["user"])
		if created_by == "Guest":
			created_by = "Administrator"

		args = {
			"first_name": self.first_name or self.last_name or "user",
			"user": self.name,
			"title": subject,
			"login_url": get_url(),
			"created_by": created_by,
		}

		args.update(add_args)

		sender = (
			frappe.session.user not in STANDARD_USERS and get_formatted_email(frappe.session.user) or None
		)

		frappe.sendmail(
			recipients=self.email,
			sender=sender,
			subject=subject,
			template=template,
			args=args,
			header=[subject, "green"],
			delayed=(not now) if now is not None else self.flags.delay_emails,
			retry=3,
		)


	

	def validate(self):

		if not frappe.flags.in_test:
			self.password_strength_test()

	@deprecated
	def validate_roles(self):
		self.populate_role_profile_roles()

	def validate_allowed_modules(self):
		if self.module_profile:
			module_profile = frappe.get_doc("Module Profile", self.module_profile)
			self.set("block_modules", [])
			for d in module_profile.get("block_modules"):
				self.append("block_modules", {"module": d.module})

	def validate_user_image(self):
		if self.user_image and len(self.user_image) > 2000:
			frappe.throw(_("Not a valid User Image."))

	def on_update(self):
		self.check_user_exists()
		

	def check_user_exists(self):
		role=[]
		if(self.role == "User"):
			for g in self.ghg:
				role.append({"role": g.project_tracking+" "+"Tracking"})
			for proj in self.project_tracking:
				role.append({"role": "Projects"})
				role.append({"role": proj.project_tracking})
			for report in self.reports:
				role.append({"role": report.project_tracking})
			
			self.insert_user(role)
		elif(self.role == "External Observer"):
			role.append({"role": "Dashboard Observer"})
			self.insert_user(role)
		elif(self.role == "Approver"):
			for g in self.ghg:
				role.append({"role": "Approver"+ " " + g.project_tracking})
			for proj in self.project_tracking:
				role.append({"role": "Approver Project"})
				role.append({"role": "Approver"+ " " + proj.project_tracking})
			for report in self.reports:
				role.append({"role":"Approver"+ " " + report.project_tracking})
			self.insert_user(role)
		else:
			for report in self.reports:
				role.append({"role":"Observer"+ " " + report.project_tracking})
			self.insert_user(role)
		

	def insert_user(self, roles):
		if frappe.db.exists("User",self.email):
			doc = frappe.get_doc("User",self.email)
			
			doc.update({
				"enabled" :self.enabled,
				"roles":roles if roles else None,
				"mobile_no": self.mobile_no,
				"first_name": self.first_name,
				"user_image": self.user_image
			})
			if self.password:
				decrypted_password = get_decrypted_password(doctype = "Approved User", name = self.name, fieldname="password", raise_exception=False)
				update_password(self.email,pwd = decrypted_password, logout_all_sessions=1)
			doc.save(ignore_permissions=True)
			frappe.db.commit()
			self.password = ""
		else:
			doc = frappe.get_doc({
				"doctype": "User",
				"name": self.email,
				"email": self.email,
				"first_name": self.first_name,
				"enabled" :self.enabled,
				"mobile_no": self.mobile_no,
				"send_welcome_email": 1,
				"roles":roles
			})
			doc.insert(ignore_permissions=True)
			doc.save(ignore_permissions=True)
			frappe.db.commit()

	@Document.hook
	def validate_reset_password(self):
		pass

	def reset_password(self, send_email=False, password_expired=False):
		from frappe.utils import get_url, random_string

		key = random_string(32)
		self.db_set("reset_password_key", key)
		self.db_set("last_reset_password_key_generated_on", now_datetime())

		url = "/update-password?key=" + key
		if password_expired:
			url = "/update-password?key=" + key + "&password_expired=true"

		link = get_url(url)
		if send_email:
			self.password_reset_mail(link)

		return link


	
	def before_rename(self, old_name, new_name, merge=False):
		frappe.clear_cache(user=old_name)
		self.validate_rename(old_name, new_name)

	def validate_rename(self, old_name, new_name):
		# do not allow renaming administrator and guest
		if old_name in STANDARD_USERS:
			throw(_("User {0} cannot be renamed").format(self.name))

		self.validate_email_type(new_name)

	def validate_email_type(self, email):
		from frappe.utils import validate_email_address

		validate_email_address(email.strip(), True)

	def after_rename(self, old_name, new_name, merge=False):
		tables = frappe.db.get_tables()
		for tab in tables:
			desc = frappe.db.get_table_columns_description(tab)
			has_fields = []
			for d in desc:
				if d.get("name") in ["owner", "modified_by"]:
					has_fields.append(d.get("name"))
			for field in has_fields:
				frappe.db.sql(
					"""UPDATE `%s`
					SET `%s` = %s
					WHERE `%s` = %s"""
					% (tab, field, "%s", field, "%s"),
					(new_name, old_name),
				)

		if frappe.db.exists("Notification Settings", old_name):
			frappe.rename_doc("Notification Settings", old_name, new_name, force=True, show_alert=False)

		# set email
		frappe.db.update("User", new_name, "email", new_name)


	def validate_username(self):
		if not self.username and self.is_new() and self.first_name:
			self.username = frappe.scrub(self.first_name)

		if not self.username:
			return

		# strip space and @
		self.username = self.username.strip(" @")

		if self.username_exists():
			if self.user_type == "System User":
				frappe.msgprint(_("Username {0} already exists").format(self.username))
				self.suggest_username()

			self.username = ""

	def password_strength_test(self):
		"""test password strength"""
		if self.flags.ignore_password_policy:
			return

	

	def suggest_username(self):
		def _check_suggestion(suggestion):
			if self.username != suggestion and not self.username_exists(suggestion):
				return suggestion

			return None

		# @firstname
		username = _check_suggestion(frappe.scrub(self.first_name))

		if not username:
			# @firstname_last_name
			username = _check_suggestion(
				frappe.scrub("{} {}".format(self.first_name, self.last_name or ""))
			)

		if username:
			frappe.msgprint(_("Suggested Username: {0}").format(username))

		return username

	def username_exists(self, username=None):
		return frappe.db.get_value(
			"User", {"username": username or self.username, "name": ("!=", self.name)}
		)


@frappe.whitelist(allow_guest=True)
def test_password_strength(new_password, key=None, old_password=None, user_data=None):
	from frappe.utils.password_strength import test_password_strength as _test_password_strength

	password_policy = (
		frappe.db.get_value(
			"System Settings", None, ["enable_password_policy", "minimum_password_score"], as_dict=True
		)
		or {}
	)

	enable_password_policy = cint(password_policy.get("enable_password_policy", 0))
	minimum_password_score = cint(password_policy.get("minimum_password_score", 0))

	if not enable_password_policy:
		return {}

	if not user_data:
		user_data = frappe.db.get_value(
			"User", frappe.session.user, ["first_name", "email"]
		)

	if new_password:
		result = _test_password_strength(new_password, user_inputs=user_data)
		password_policy_validation_passed = False

		# score should be greater than 0 and minimum_password_score
		if result.get("score") and result.get("score") >= minimum_password_score:
			password_policy_validation_passed = True

		result["feedback"]["password_policy_validation_passed"] = password_policy_validation_passed
		return result

@frappe.whitelist()
def verify_password(password):
	frappe.local.login_manager.check_password(frappe.session.user, password)


@frappe.whitelist(allow_guest=True)
@rate_limit(limit=get_password_reset_limit, seconds=24 * 60 * 60, methods=["POST"])
def reset_password(user):
	if user == "Administrator":
		return "not allowed"

	try:
		user = frappe.get_doc("User", user)
		if not user.enabled:
			return "disabled"

		user.validate_reset_password()
		user.reset_password(send_email=True)

		return frappe.msgprint(
			msg=_("Password reset instructions have been sent to your email"),
			title=_("Password Email Sent"),
		)
	except frappe.DoesNotExistError:
		frappe.log_error("Error in Approved User", frappe.get_traceback())
		frappe.local.response["http_status_code"] = 404
		frappe.clear_messages()
		return "not found"



def get_query_conditions(user):
	
	if "System Manager" not in frappe.get_roles(user) and "MRV Admin" not in frappe.get_roles(user):
		return f"""(`tabApproved User` .name = '{user}')"""