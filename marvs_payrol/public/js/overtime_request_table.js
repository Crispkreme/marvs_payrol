frappe.ready(function () {

    let employee = JSON.parse(localStorage.getItem("employee"));

    if (!employee) {
        window.location.href = "/login";
        return;
    }

    frappe.call({
        method: "marvs_payrol.www.overtime_request_table.get_ot_requests",
        args: {
            employee: employee.employee_id
        },
        callback: function (r) {

            let data = r.message || [];

            let html = "";

            if (!data.length) {
                html = `<tr><td colspan="8">No OT requests found</td></tr>`;
            } else {

                data.forEach(d => {

                    html += `
                        <tr>
                            <td>${d.employee || ""}</td>
                            <td>${d.attendance_date || ""}</td>
                            <td>${d.overtime_type || ""}</td>
                            <td>${d.start_time || ""}</td>
                            <td>${d.end_time || ""}</td>
                            <td>${d.requested_hours || 0}</td>
                            <td>${d.status || ""}</td>
                            <td>${d.reason || ""}</td>
                        </tr>
                    `;
                });
            }

            document.getElementById("otTable").innerHTML = html;
        }
    });

});