# Copyright (c) 2026, Marvin Ramos and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class PMSEmployee(Document):

    def before_insert(self):
        if not self.user:
            self.user = frappe.session.user

    def validate(self):
        self.full_name = " ".join(filter(None, [
            self.first_name,
            self.middle_name,
            self.last_name
        ]))

    # =========================
    # AUTO CREATE ATTENDANCE REPORT
    # =========================
    def after_insert(self):

        if frappe.db.exists("PMS-Attendance Report", {"employee": self.name}):
            return

        frappe.get_doc({
            "doctype": "PMS-Attendance Report",
            "employee": self.name,
            "status": "Active",
            "day_shift_hrs": 0,
            "night_shift_hrs": 0,
            "overtime_hrs": 0,
            "night_overtime_hrs": 0,
            "regular_holiday": 0,
            "regular_holiday_ot": 0,
            "special_holiday": 0,
            "special_holiday_ot": 0,
            "rest_day": 0,
            "rest_day_ot": 0,
            "absent": 0,
            "leave": 0
        }).insert(ignore_permissions=True)