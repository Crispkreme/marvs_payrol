import frappe

@frappe.whitelist(allow_guest=True)
def get_leave_requests(employee):
    data = frappe.get_all(
        "PMS-Leave Request",
        filters={"employee": employee},
        fields=[
            "name",
            "employee_name",
            "leave_type",
            "total_days",
            "from_date",
            "to_date",
            "status",
            "reason"
        ],
        order_by="creation desc"
    )

    return data