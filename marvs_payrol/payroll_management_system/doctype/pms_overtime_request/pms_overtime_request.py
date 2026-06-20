# Copyright (c) 2026, Marvin Ramos and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import time_diff_in_hours


class PMSOvertime(Document):

    def validate(self):

        if self.start_time and self.end_time:
            self.requested_hours = round(
                time_diff_in_hours(self.end_time, self.start_time),
                2
            )

    # ======================================================
    # TRIGGER WHEN STATUS CHANGES (APPROVED)
    # ======================================================
    def on_update(self):

        if self.status == "Approved":
            self.apply_overtime()

        elif self.status == "Rejected":
            self.remove_overtime()

    # ======================================================
    # APPLY OT TO ATTENDANCE
    # ======================================================
    def apply_overtime(self):

        attendance_name = frappe.db.get_value(
            "PMS-Employee Attendance Log",
            {
                "employee": self.employee,
                "attendance_date": self.attendance_date
            },
            "name"
        )

        if not attendance_name:
            return

        doc = frappe.get_doc("PMS-Employee Attendance Log", attendance_name)

        # mark approved
        doc.overtime_approved = 1

        # SAFE ADDITION (IMPORTANT)
        doc.total_overtime_hours = (doc.total_overtime_hours or 0) + (self.requested_hours or 0)

        doc.save(ignore_permissions=True)
        frappe.db.commit()

    # ======================================================
    # REMOVE OT IF CANCELLED/REJECTED
    # ======================================================
    def remove_overtime(self):

        attendance_name = frappe.db.get_value(
            "PMS-Employee Attendance Log",
            {
                "employee": self.employee,
                "attendance_date": self.attendance_date
            },
            "name"
        )

        if not attendance_name:
            return

        doc = frappe.get_doc("PMS-Employee Attendance Log", attendance_name)

        doc.overtime_approved = 0

        # subtract OT safely
        doc.total_overtime_hours = max(
            (doc.total_overtime_hours or 0) - (self.requested_hours or 0),
            0
        )

        doc.save(ignore_permissions=True)
        frappe.db.commit()