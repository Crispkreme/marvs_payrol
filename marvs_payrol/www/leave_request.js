frappe.ready(() => {

    $("#submit").click(() => {

        frappe.call({
            method: "marvs_payrol.www.leave_request.create_leave",
            args: {
                employee: $("#employee").val(),
                leave_type: $("#leave_type").val(),
                from_date: $("#from_date").val(),
                to_date: $("#to_date").val(),
                reason: $("#reason").val()
            },
            callback: function(r) {

                if (r.message.success) {
                    $("#message").html(`
                        <div class="alert alert-success">
                            Leave request submitted successfully
                        </div>
                    `);
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