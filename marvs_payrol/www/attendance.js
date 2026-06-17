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

                if (r.message) {
                    $("#employee-name").text(r.message.employee_name || "-");
                } else {
                    $("#employee-name").text("-");
                }
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

                let rows = "";

                let data = r.message || [];

                if (!Array.isArray(data)) {
                    data = [];
                }

                if (data.length === 0) {
                    $("#history-body").html(`
                        <tr>
                            <td colspan="7" class="text-center text-muted">
                                No attendance records
                            </td>
                        </tr>
                    `);
                    return;
                }

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

        let employee = $("#employee").val();

        if (!employee) {
            $("#message").html(`
                <div class="alert alert-warning">
                    Please enter Employee ID
                </div>
            `);
            return;
        }

        // prevent spam clicks
        $("#attendance-btn").prop("disabled", true);

        frappe.call({
            method: "marvs_payrol.www.attendance.record_attendance",
            args: { employee: employee },
            callback: function (r) {

                if (!r.message) return;

                // =========================
                // SHOW MESSAGE ONLY
                // =========================
                if (r.message.success) {

                    $("#message").html(`
                        <div class="alert alert-success">
                            ${r.message.message}
                        </div>
                    `);

                    $("#status").text(r.message.status || "-");
                    $("#hours").text(r.message.total_hours || 0);

                } else {

                    $("#message").html(`
                        <div class="alert alert-warning">
                            ${r.message.message}
                        </div>
                    `);
                }

                // =========================
                // 🔥 ALWAYS LOAD HISTORY (IMPORTANT FIX)
                // =========================
                load_history(employee);
                load_employee(employee);
            }
        });
    });


    // =========================
    // EMPLOYEE INPUT CHANGE
    // =========================
    $("#employee").on("change", function () {

        let employee = $(this).val().trim();

        if (!employee) return;

        // prevent duplicate calls
        if (current_employee === employee) return;

        current_employee = employee;

        $("#history-body").html("");
        $("#employee-name").text("-");

        load_employee(employee);
        load_history(employee);
    });

});