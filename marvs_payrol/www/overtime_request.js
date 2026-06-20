function updateDateTime() {

    let now = new Date();

    let options = {
        weekday: "long",
        year: "numeric",
        month: "long",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit"
    };

    $("#current_datetime").text(
        now.toLocaleString("en-US", options)
    );
}

frappe.ready(() => {

    let current_employee = null;
    
    updateDateTime();
    setInterval(updateDateTime, 1000);

    // =========================
    // LOAD EMPLOYEE INFO
    // =========================
    function load_employee(employee) {

        frappe.call({
            method: "marvs_payrol.www.leave_request.get_employee_info",
            args: { employee: employee },

            callback: function (r) {

                if (r.message && r.message.success) {

                    $("#employee-name").text(r.message.data.employee_name);
                    $("#employee-status").text(r.message.data.employee_status || "-");

                } else {

                    $("#employee-name").text("-");
                    $("#employee-status").text("-");

                }
            }
        });
    }

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
        $("#employee-status").text("-");

        load_employee(employee);
    });

    // =====================================================
    // SUBMIT OVERTIME
    // =====================================================
    $("#submit_btn").click(function () {

        let employee = $("#employee").val();
        let attendance_date = $("#attendance_date").val();
        let start_time = $("#start_time").val();
        let end_time = $("#end_time").val();
        let reason = $("#reason").val();

        // =========================
        // VALIDATION
        // =========================
        if (!employee || !attendance_date || !start_time || !end_time || !reason) {
            $("#message").css("color", "red").text("Please fill all fields.");
            return;
        }

        if (end_time <= start_time) {
            $("#message").css("color", "red").text("End time must be greater than start time.");
            return;
        }

        // =========================
        // LOADING
        // =========================
        $("#submit_btn").prop("disabled", true).text("Submitting...");

        frappe.call({
            method: "marvs_payrol.www.overtime_request.submit_overtime",
            args: {
                employee: employee,
                attendance_date: attendance_date,
                start_time: start_time,
                end_time: end_time,
                reason: reason
            },
            callback: function (r) {

                $("#submit_btn").prop("disabled", false).text("Submit Overtime Request");

                if (r.message && r.message.success) {

                    $("#message")
                        .css("color", "green")
                        .text(r.message.message);

                    // clear form
                    $("#attendance_date").val("");
                    $("#start_time").val("");
                    $("#end_time").val("");
                    $("#reason").val("");

                } else {
                    $("#message")
                        .css("color", "red")
                        .text(r.message?.message || "Failed to submit request.");
                }
            },

            error: function () {
                $("#submit_btn").prop("disabled", false).text("Submit Overtime Request");

                $("#message")
                    .css("color", "red")
                    .text("Server error occurred.");
            }
        });

    });

});