console.log("EMPLOYEE LOGIN JS LOADED");

document.getElementById("employee_login_btn").addEventListener("click", function() {
    alert("Button works");
});

document.addEventListener("DOMContentLoaded", function () {

    const form = document.getElementById("employee-login-form");
    const btn = document.getElementById("employee_login_btn");
    const msg = document.getElementById("msg");

    if (!btn) {
        console.error("Button not found");
        return;
    }

    // Stop ALL form submissions
    form.addEventListener("submit", function(e) {
        e.preventDefault();
        e.stopPropagation();
        return false;
    });

    btn.addEventListener("click", function(e) {

        e.preventDefault();
        e.stopPropagation();

        console.log("LOGIN CLICKED");

        let email = document.getElementById("email").value.trim();
        let password = document.getElementById("password").value.trim();

        frappe.call({
            method: "marvs_payrol.www.employee_login.employee_login",
            args: {
                email: email,
                password: password
            },
            callback: function(r) {

                console.log(r);

                if (!r.message) {
                    msg.innerHTML = "Invalid Email or Employee ID";
                    msg.style.color = "red";
                    return;
                }

                localStorage.setItem(
                    "employee",
                    JSON.stringify(r.message)
                );

                msg.innerHTML = "Login Success";
                msg.style.color = "green";

                setTimeout(() => {
                    window.location.href = "/dashboard";
                }, 1000);
            }
        });

        return false;
    });

});