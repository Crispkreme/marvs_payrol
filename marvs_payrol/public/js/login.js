console.log("LOGIN JS LOADED");

document.addEventListener("DOMContentLoaded", function () {

    const btn = document.getElementById("loginBtn");

    console.log("LOGIN BUTTON:", btn);

    if (!btn) {
        console.error("Login button not found");
        return;
    }

    btn.addEventListener("click", function () {

        console.log("LOGIN CLICKED");

        let email = document.getElementById("email").value;
        let password = document.getElementById("password").value;
        let msg = document.getElementById("msg");

        msg.innerText = "Logging in...";
        msg.style.color = "black";

        frappe.call({
            method: "marvs_payrol.www.login.employee_login",
            args: {
                email: email,
                password: password
            },
            callback: function (r) {

                console.log("LOGIN RESPONSE:", r);

                if (!r.message) {
                    msg.innerText = "Invalid login";
                    msg.style.color = "red";
                    return;
                }

                msg.innerText = "Success";
                msg.style.color = "green";

                localStorage.setItem("employee", JSON.stringify(r.message));

                setTimeout(() => {
                    window.location.href = "/dashboard";
                }, 800);
            }
        });
    });
});