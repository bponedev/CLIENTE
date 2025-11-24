/* =======================================================
   Mostrar / Ocultar Senha
========================================================== */

function togglePassword() {
    const input = document.getElementById("password-field");
    input.type = input.type === "password" ? "text" : "password";
}

/* =======================================================
   Selecionar Todos na Tabela
========================================================== */

function toggleSelectAll(master) {
    const checkboxes = document.querySelectorAll('input[type="checkbox"][name="ids"]');
    checkboxes.forEach(cb => cb.checked = master.checked);
}

/* =======================================================
   Sumir com flash messages após 5s
========================================================== */

setTimeout(() => {
    document.querySelectorAll('.flash').forEach(el => {
        el.style.transition = "0.5s";
        el.style.opacity = 0;
        setTimeout(() => el.remove(), 500);
    });
}, 5000);
