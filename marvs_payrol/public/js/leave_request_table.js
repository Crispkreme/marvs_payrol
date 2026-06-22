frappe.ready(function () {

    let employee = JSON.parse(localStorage.getItem("employee"));

    if (!employee) {
        window.location.href = "/login";
        return;
    }

    frappe.call({
        method: "marvs_payrol.www.leave_request_table.get_leave_requests",
        args: {
            employee: employee.employee_id
        },
        callback: function (r) {

            let rows = r.message || [];

            let html = "";

            if (rows.length === 0) {
                html = `<tr><td colspan="7">No leave requests found</td></tr>`;
            } else {

                rows.forEach(d => {

                    html += `
                        <tr>
                            <td>${d.employee_name || ""}</td>
                            <td>${d.leave_type || ""}</td>
                            <td>${d.total_days || 0}</td>
                            <td>${d.from_date || ""}</td>
                            <td>${d.to_date || ""}</td>
                            <td>${d.status || ""}</td>
                            <td>${d.reason || ""}</td>
                        </tr>
                    `;
                });
            }

            document.getElementById("leaveTable").innerHTML = html;
        }
    });

});