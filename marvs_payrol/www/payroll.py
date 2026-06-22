import frappe

@frappe.whitelist(allow_guest=True)
def get_payroll_slip(employee, payroll_period=None):

    # Build filters
    filters = {
        "employee": employee
    }

    if payroll_period:
        filters["payroll_period"] = payroll_period

    # Get latest payroll entry (or specific period)
    payroll = frappe.db.get_value(
        " PMS-Payroll Entry",
        filters,
        [
            "name",
            "employee",
            "employee_name",
            "employment_status",
            "payroll_period",

            "basic_pay",
            "allowance",
            "daily_rate",
            "hourly_rate",

            "overtime_pay",
            "deduction",
            "net_pay",

            "sss_deduction",
            "pagibig_deduction",
            "philhealth_deduction",
            "tin_deduction",

            "total_work_hr",
            "total_overtime_min",
            "total_late_min",
            "total_absent",

            "total_work_hr_display",
            "total_overtime_display",
            "total_late_display",
            "total_absent_display"
        ],
        as_dict=True
    )

    if not payroll:
        return {}

    return payroll