# Copyright (c) 2026, Marvin Ramos and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt


class PMSLeaveRequest(Document):

    def on_update(self):
        update_leave_to_attendance(self)

def update_leave_to_attendance(doc):
    try:
        # Only process approved leave requests
        if doc.status != "Approved":
            return

        if not doc.employee:
            return

        # Prevent duplicate processing
        if doc.leave_applied_to_attendance:
            return

        total_days = flt(doc.total_days)

        if total_days <= 0:
            return

        # Get Attendance Report
        report_name = frappe.db.get_value(
            "PMS-Attendance Report",
            {"employee": doc.employee},
            "name"
        )

        if not report_name:
            frappe.msgprint(
                f"No Attendance Report found for employee {doc.employee}"
            )
            return

        report = frappe.get_doc(
            "PMS-Attendance Report",
            report_name
        )

        # Add leave days
        report.leave = flt(report.leave) + total_days

        report.save(ignore_permissions=True)

        # Mark this leave request as already processed
        doc.db_set("leave_applied_to_attendance", 1)

        frappe.db.commit()

        frappe.msgprint(
            f"Successfully added {total_days} leave day(s) to Attendance Report."
        )

    except Exception:
        frappe.log_error(
            frappe.get_traceback(),
            "LEAVE TO ATTENDANCE ERROR"
        )
