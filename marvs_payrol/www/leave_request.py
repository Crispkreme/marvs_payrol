import frappe

@frappe.whitelist(allow_guest=True)
def create_leave(employee, leave_type, from_date, to_date, reason):

    if not employee:
        return {"success": False, "message": "Employee required"}

    doc = frappe.get_doc({
        "doctype": "PMS-Leave Request",
        "employee": employee,
        "leave_type": leave_type,
        "from_date": from_date,
        "to_date": to_date,
        "reason": reason,
        "status": "Pending"
    })

    doc.insert(ignore_permissions=True)

    frappe.db.commit()

    return {
        "success": True,
        "message": "Leave request created"
    }