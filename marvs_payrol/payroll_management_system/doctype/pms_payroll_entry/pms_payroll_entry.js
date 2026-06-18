// Copyright (c) 2026, Marvin Ramos and contributors
// For license information, please see license.txt

frappe.ui.form.on("PMS-Payroll Entry", {

    employee(frm) {

        if (!frm.doc.employee) return;

        frappe.db.get_doc("PMS-Employee", frm.doc.employee)
        .then(emp => {

            if (!emp) return;

            // =========================
            // BASIC PAY
            // =========================
            frm.set_value("basic_pay", emp.basic_salary || 0);
            frm.set_value("allowance", emp.allowance || 0);
            frm.set_value("employment_status", emp.employment_status);

            // =========================
            // GET CONTRIBUTIONS FROM EMPLOYEE
            // =========================
            let sss = emp.sss_contribution || 0;
            let philhealth = emp.philhealth_contribution || 0;
            let pagibig = emp.pagibig_contribution || 0;
            let tin = emp.tin_contribution || 0;

            // =========================
            // RULE: OJT / TRAINEE = NO DEDUCTIONS
            // =========================
            const no_deduction = ["OJT", "Trainee"];

            if (no_deduction.includes(emp.employment_status)) {

                sss = 0;
                philhealth = 0;
                pagibig = 0;
                tin = 0;

                frm.toggle_display("deduction_summary_section", false);

            } else {

                frm.toggle_display("deduction_summary_section", true);
            }

            // =========================
            // PASS TO PAYROLL FIELDS
            // =========================
            frm.set_value("sss_deduction", sss);
            frm.set_value("philhealth_deduction", philhealth);
            frm.set_value("pagibig_deduction", pagibig);
            frm.set_value("tin_deduction", tin);

            // refresh UI
            frm.refresh_fields([
                "sss_deduction",
                "philhealth_deduction",
                "pagibig_deduction",
                "tin_deduction"
            ]);

        });

    }
});