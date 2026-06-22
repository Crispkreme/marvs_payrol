window.format_hours = function (hours) {
    let total_minutes = Math.round(Number(hours || 0) * 60);

    let h = Math.floor(total_minutes / 60);
    let m = total_minutes % 60;

    return `${h}h ${m}m`;
};

frappe.ready(function () {

    let employee = JSON.parse(localStorage.getItem("employee"));

    if (!employee) {
        window.location.href = "/login";
        return;
    }

    // =========================
    // SET WELCOME NAME
    // =========================
    document.getElementById("emp_name").innerText =
        employee.full_name || "Employee";

    // =========================
    // DASHBOARD DATA
    // =========================
    frappe.call({
        method: "marvs_payrol.www.dashboard.get_employee_dashboard",
        args: {
            employee: employee.employee_id
        },
        callback: function (r) {

            console.log("DASHBOARD DATA:", r.message);

            let d = r.message || {};

            let work = d.total_work_hr || d.work_hours || 0;
            let ot = d.total_ot || d.ot_hours || 0;
            let late = d.total_late || d.late || 0;
            let absent = d.total_absent || d.absent || 0;
            let leave = d.total_leave || d.leave || 0;

            document.getElementById("work").innerText = format_hours(work);
            document.getElementById("ot").innerText = format_hours(ot);
            document.getElementById("late").innerText = format_hours(late / 60);
            document.getElementById("absent").innerText = `${absent} day(s)`;
            document.getElementById("leave").innerText = `${leave} day(s)`;
        }
    });
});


// =========================
// LOGOUT
// =========================
function logout() {

    frappe.call({
        method: "marvs_payrol.api.login.employee_logout",
        callback: function () {

            localStorage.removeItem("employee");
            window.location.href = "/login";
        }
    });
}