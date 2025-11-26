// Alternar visibilidade da senha
function togglePassword() {
    let input = document.getElementById("senha_input");

    if (!input) return;

    if (input.type === "password") {
        input.type = "text";
    } else {
        input.type = "password";
    }
}


// Confirmação de exclusão (universal)
function confirmarExclusao(event, mensagem = "Tem certeza que deseja excluir?") {
    if (!confirm(mensagem)) {
        event.preventDefault();
        return false;
    }
    return true;
}


// Mascara simples para CPF
function mascaraCPF(input) {
    let v = input.value.replace(/\D/g, "");

    if (v.length > 3) v = v.replace(/^(\d{3})(\d)/, "$1.$2");
    if (v.length > 6) v = v.replace(/^(\d{3})\.(\d{3})(\d)/, "$1.$2.$3");
    if (v.length > 9) v = v.replace(/\.(\d{3})(\d)/, ".$1-$2");

    input.value = v;
}


// Aplica máscara automaticamente
document.addEventListener("input", function(e) {
    if (e.target.name === "cpf") {
        mascaraCPF(e.target);
    }
});
