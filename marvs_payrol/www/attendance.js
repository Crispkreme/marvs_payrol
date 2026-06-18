frappe.ready(() => {

    let current_employee = null;

    // =========================
    // LOAD EMPLOYEE INFO
    // =========================
    function load_employee(employee) {

        frappe.call({
            method: "marvs_payrol.www.attendance.get_employee_info",
            args: { employee: employee },
            callback: function (r) {
                $("#employee-name").text(r.message?.employee_name || "-");
            }
        });
    }


    // =========================
    // LOAD HISTORY
    // =========================
    function load_history(employee) {

        frappe.call({
            method: "marvs_payrol.www.attendance.get_attendance_history",
            args: { employee: employee },
            callback: function (r) {

                let data = r.message || [];

                if (!Array.isArray(data)) data = [];

                if (data.length === 0) {
                    $("#history-body").html(`
                        <tr>
                            <td colspan="9" class="text-center text-muted">
                                No attendance records
                            </td>
                        </tr>
                    `);
                    return;
                }

                let rows = "";

                data.forEach(row => {

                    rows += `
                        <tr>
                            <td>${row.attendance_date || "-"}</td>
                            <td>${row.status || "-"}</td>
                            <td>${row.am_time_in || "-"}</td>
                            <td>${row.am_time_out || "-"}</td>
                            <td>${row.pm_time_in || "-"}</td>
                            <td>${row.pm_time_out || "-"}</td>
                            <td>${row.total_work_hours || 0}</td>
                            <td>${row.late_minute || 0}</td>
                            <td>${row.total_overtime_hours || 0}</td>
                        </tr>
                    `;
                });

                $("#history-body").html(rows);
            }
        });
    }


    // =========================
    // RECORD ATTENDANCE
    // =========================
    $("#attendance-btn").click(function () {

        let employee = $("#employee").val().trim();

        if (!employee) {
            $("#message").html(`
                <div class="alert alert-warning">
                    Please enter Employee ID
                </div>
            `);
            return;
        }

        let payload = {
            employee: employee,
            am_time_in: $("#am_time_in").val(),
            am_time_out: $("#am_time_out").val(),
            pm_time_in: $("#pm_time_in").val(),
            pm_time_out: $("#pm_time_out").val()
        };

        $("#attendance-btn").prop("disabled", true);

        frappe.call({
            method: "marvs_payrol.www.attendance.record_attendance",
            args: payload,
            callback: function (r) {

                $("#attendance-btn").prop("disabled", false);

                if (!r.message) return;

                if (r.message.success) {

                    $("#message").html(`
                        <div class="alert alert-success">
                            ${r.message.message}
                        </div>
                    `);

                    // =========================
                    // LIVE SUMMARY (UPDATED)
                    // =========================
                    $("#status").text(r.message.status || "-");
                    $("#hours").text(r.message.total_work_hours || 0);

                } else {

                    $("#message").html(`
                        <div class="alert alert-warning">
                            ${r.message.message}
                        </div>
                    `);
                }

                load_history(employee);
                load_employee(employee);
            }
        });
    });


    // =========================
    // EMPLOYEE CHANGE
    // =========================
    $("#employee").on("change", function () {

        let employee = $(this).val().trim();

        if (!employee) return;

        if (current_employee === employee) return;

        current_employee = employee;

        $("#history-body").html("");
        $("#employee-name").text("-");

        load_employee(employee);
        load_history(employee);
    });

});