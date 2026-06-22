import frappe

@frappe.whitelist(allow_guest=True)
def get_ot_requests(employee):

    return frappe.get_all(
        "PMS-Overtime Request",
        filters={"employee": employee},
        fields=[
            "employee",
            "attendance_date",
            "start_time",
            "end_time",
            "requested_hours",
            "status",
            "overtime_type",
            "reason"
        ],
        order_by="creation desc"
    )