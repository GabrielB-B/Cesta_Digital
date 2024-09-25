document.addEventListener("DOMContentLoaded", function() {
    const form = document.querySelector("form");

    if (form) {
        form.addEventListener("submit", function(event) {
            const inputs = form.querySelectorAll("input");
            let valid = true;

            inputs.forEach(function(input) {
                if (input.required && input.value.trim() === "") {
                    valid = false;
                    alert("Por favor, preencha todos os campos obrigatórios.");
                }
            });

            if (!valid) {
                event.preventDefault();
            }
        });
    }

    const logoutButton = document.querySelector("button.logout");
    if (logoutButton) {
        logoutButton.addEventListener("click", function() {
            window.location.href = "/logout";
        });
    }
});
