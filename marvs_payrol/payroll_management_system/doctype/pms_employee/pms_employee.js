// Copyright (c) 2026, Marvin Ramos and contributors
// For license information, please see license.txt

frappe.ui.form.on("PMS-Employee", {

    refresh(frm) {
        compute_deductions(frm);
        calculate_daily_hourly_rate(frm);
        toggle_contract_date(frm);
    },

    basic_salary(frm) {
        compute_deductions(frm);
        calculate_daily_hourly_rate(frm);
    },

    employment_status(frm) {
        compute_deductions(frm);
        calculate_daily_hourly_rate(frm);
    },

    not_contractual(frm) {
        toggle_contract_date(frm);
    }

});

// =========================
// CONTRACT TOGGLE
// =========================
function toggle_contract_date(frm) {

    let is_not_contractual = frm.doc.not_contractual ? 1 : 0;

    if (is_not_contractual) {

        frm.set_df_property('contract_end_date', 'read_only', 1);
        frm.set_df_property('contract_end_date', 'reqd', 0);
        frm.set_value('contract_end_date', null);

    } else {

        frm.set_df_property('contract_end_date', 'read_only', 0);
        frm.set_df_property('contract_end_date', 'reqd', 1);
    }

    frm.refresh_field('contract_end_date');
}

// =========================
// DEDUCTION COMPUTATION
// =========================
function compute_deductions(frm) {

    let salary = frm.doc.basic_salary || 0;
    let status = frm.doc.employment_status;

    const no_deduction = ["OJT", "Trainee"];

    let sss = 0;
    let philhealth = 0;
    let pagibig = 0;
    let tin = 0;

    if (!no_deduction.includes(status)) {

        // =========================
        // SIMPLE PH RULES (MVP)
        // =========================

        // SSS approx 4.5%
        sss = salary * 0.045;

        // PhilHealth approx 2.5%
        philhealth = salary * 0.025;

        // Pag-IBIG fixed cap
        pagibig = salary >= 1500 ? 200 : 100;

        // Tax placeholder
        tin = salary * 0.02;
    }

    frm.set_value("sss_contribution", round2(sss));
    frm.set_value("philhealth_contribution", round2(philhealth));
    frm.set_value("pagibig_contribution", round2(pagibig));
    frm.set_value("tin_contribution", round2(tin));

    frm.refresh_fields([
        "sss_contribution",
        "philhealth_contribution",
        "pagibig_contribution",
        "tin_contribution"
    ]);
}

// =========================
// HELPER
// =========================
function round2(val) {
    return Math.round((val || 0) * 100) / 100;
}

// =========================
// COMPUTATION FOR DAILY AND HOURLY RATE
// =========================
function calculate_daily_hourly_rate(frm) {

    let salary = frm.doc.basic_salary;

    if (!salary) {
        frm.set_value("daily_rate", 0);
        frm.set_value("hourly_rate", 0);
        return;
    }

    let daily = salary / 26;
    let hourly = daily / 8;

    frm.set_value("daily_rate", flt(daily, 2));
    frm.set_value("hourly_rate", flt(hourly, 2));
}