frappe.ready(function () {

    let employee = JSON.parse(localStorage.getItem("employee"));

    if (!employee) {
        window.location.href = "/login";
        return;
    }

    frappe.call({
        method: "marvs_payrol.www.dashboard.get_employee_dashboard",
        args: {
            employee: employee.employee_id
        },
        callback: function (r) {

            let d = r.message || {};

            // Employee Info
            document.getElementById("employee").innerText = employee.employee_id;
            document.getElementById("employee_name").innerText = employee.full_name;
            document.getElementById("employment_status").innerText = employee.status || "-";
            document.getElementById("payroll_period").innerText = d.payroll_period || "Current Month";

            // Salary
            document.getElementById("basic_pay").innerText = d.basic_pay || 0;
            document.getElementById("allowance").innerText = d.allowance || 0;
            document.getElementById("daily_rate").innerText = d.daily_rate || 0;
            document.getElementById("hourly_rate").innerText = d.hourly_rate || 0;

            document.getElementById("overtime_pay").innerText = d.total_ot || 0;
            document.getElementById("deduction").innerText = d.total_deduction || 0;
            document.getElementById("net_pay").innerText = d.net_pay || 0;

            // Contributions
            document.getElementById("sss_deduction").innerText = d.sss || 0;
            document.getElementById("pagibig_deduction").innerText = d.pagibig || 0;
            document.getElementById("philhealth_deduction").innerText = d.philhealth || 0;
            document.getElementById("tin_deduction").innerText = d.tin || 0;

            // Attendance
            document.getElementById("work").innerText = d.total_work_hr || 0;
            document.getElementById("ot").innerText = d.total_ot || 0;
            document.getElementById("late").innerText = d.total_late || 0;
            document.getElementById("absent").innerText = d.total_absent || 0;
        }
    });

});