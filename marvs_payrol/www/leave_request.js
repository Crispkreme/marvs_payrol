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

    // =========================
    // SUBMIT LEAVE REQUEST
    // =========================
    $("#submit").click(function (e) {

        e.preventDefault();

        let data = {
            employee: $("#employee").val(),
            employee_name: $("#employee-name").text(),
            leave_type: $("#leave_type").val(),
            from_date: $("#from_date").val(),
            to_date: $("#to_date").val(),
            reason: $("#reason").val()
        };

        if (!data.employee || !data.leave_type || !data.from_date || !data.to_date) {
            $("#message").html(`
                <div class="alert alert-danger">
                    Please fill all required fields
                </div>
            `);
            return;
        }

        $("#submit").prop("disabled", true).text("Submitting...");

        frappe.call({
            method: "marvs_payrol.www.leave_request.create_leave",
            args: data,

            callback: function (r) {

                $("#submit").prop("disabled", false).text("Submit Leave Request");

                if (r.message && r.message.success) {

                    $("#message").html(`
                        <div class="alert alert-success">
                            ${r.message.message}
                        </div>
                    `);

                    // RESET FORM
                    $("#employee").val("");
                    $("#employee-name").text("-");
                    $("#employee-status").text("-");
                    $("#leave_type").prop("selectedIndex", 0);
                    $("#from_date").val("");
                    $("#to_date").val("");
                    $("#reason").val("");

                    setTimeout(() => {
                        window.location.href = "/leave-request-table";
                    }, 1000);

                } else {

                    $("#message").html(`
                        <div class="alert alert-danger">
                            ${r.message.message}
                        </div>
                    `);

                }
            }
        });

    });

});