frappe.ui.form.on("PMS-Payroll Entry", {

    employee(frm) {

        if (!frm.doc.employee) return;

        frappe.db.get_doc("PMS-Employee", frm.doc.employee)
        .then(emp => {

            if (!emp) return;

            // =====================================
            // BASIC PAY
            // =====================================
            frm.set_value("basic_pay", emp.basic_salary || 0);
            frm.set_value("allowance", emp.allowance || 0);
            frm.set_value("employment_status", emp.employment_status);

            // =====================================
            // DAILY + HOURLY RATE (NEW)
            // =====================================
            let daily_rate = (emp.basic_salary || 0) / 22;
            let hourly_rate = daily_rate / 8;

            // frm.set_value("daily_rate", daily_rate);
            // frm.set_value("hourly_rate", hourly_rate);

            // =====================================
            // GOVERNMENT CONTRIBUTIONS
            // =====================================
            let sss = emp.sss_contribution || 0;
            let philhealth = emp.philhealth_contribution || 0;
            let pagibig = emp.pagibig_contribution || 0;
            let tin = emp.tin_contribution || 0;

            const no_deduction = ["OJT", "Trainee"];

            if (no_deduction.includes(emp.employment_status)) {

                sss = philhealth = pagibig = tin = 0;
                frm.toggle_display("deduction_summary_section", false);

            } else {
                frm.toggle_display("deduction_summary_section", true);
            }

            frm.set_value("sss_deduction", sss);
            frm.set_value("philhealth_deduction", philhealth);
            frm.set_value("pagibig_deduction", pagibig);
            frm.set_value("tin_deduction", tin);

            compute_net_pay(frm);
        });

        // =====================================
        // ATTENDANCE SUMMARY
        // =====================================
        frappe.call({
            method: "marvs_payrol.www.attendance.get_payroll_inputs",
            args: { employee: frm.doc.employee },

            callback: function (r) {

                if (!r.message) return;

                let d = r.message;

                // =====================================
                // AUTO OT ROUNDING (NEW)
                // =====================================
                let ot_minutes = d.overtime_hours || 0;

                // convert hours → minutes
                let ot_total_min = ot_minutes * 60;

                // ROUND TO 15 MIN BLOCKS
                let rounded_ot = Math.round(ot_total_min / 15) * 15;

                frm.set_value("total_work_hr", d.total_work_hours || 0);
                frm.set_value("total_late_min", d.late_minutes || 0);
                frm.set_value("total_overtime_min", rounded_ot / 60);
                frm.set_value("total_absent", d.absences || 0);

                compute_net_pay(frm);
            }
        });
    },

    basic_pay(frm) { compute_net_pay(frm); },
    allowance(frm) { compute_net_pay(frm); },
    overtime_pay(frm) { compute_net_pay(frm); },
    sss_deduction(frm) { compute_net_pay(frm); },
    pagibig_deduction(frm) { compute_net_pay(frm); },
    philhealth_deduction(frm) { compute_net_pay(frm); },
    tin_deduction(frm) { compute_net_pay(frm); },

    total_late_min(frm) { compute_net_pay(frm); },
    total_absent(frm) { compute_net_pay(frm); }
});


// =====================================
// COMPUTE NET PAY (FINAL LOGIC)
// =====================================
function compute_net_pay(frm) {

    // =====================================
    // INCOME
    // =====================================
    let income =
        flt(frm.doc.basic_pay) +
        flt(frm.doc.allowance) +
        flt(frm.doc.overtime_pay);

    // =====================================
    // ATTENDANCE DEDUCTIONS
    // =====================================

    let late_deduction =
        flt(frm.doc.hourly_rate) * (flt(frm.doc.total_late_min) / 60);

    let absent_deduction =
        flt(frm.doc.daily_rate) * flt(frm.doc.total_absent);

    // =====================================
    // GOVERNMENT DEDUCTIONS
    // =====================================
    let government =
        flt(frm.doc.sss_deduction) +
        flt(frm.doc.pagibig_deduction) +
        flt(frm.doc.philhealth_deduction) +
        flt(frm.doc.tin_deduction);

    // =====================================
    // TOTAL DEDUCTIONS
    // =====================================
    let total_deductions =
        government +
        late_deduction +
        absent_deduction;

    let net_pay = income - total_deductions;

    frm.set_value("deduction", total_deductions);
    frm.set_value("net_pay", net_pay);
}