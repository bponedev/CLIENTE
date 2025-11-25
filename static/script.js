/* Preview automático de TAGS */
function setupTagPreview() {
    const input = document.querySelector('input[name="tags"]');
    const preview = document.querySelector('#tag-preview');
    if (!input || !preview) return;

    function render() {
        preview.innerHTML = "";
        let tags = input.value.split(',')
                     .map(t => t.trim())
                     .filter(t => t.length > 0);

        tags.forEach(tag => {
            const span = document.createElement("span");
            span.classList.add("tag-chip");
            span.textContent = tag.toUpperCase();
            preview.appendChild(span);
        });
    }
    input.addEventListener("input", render);
    render();
}

document.addEventListener("DOMContentLoaded", setupTagPreview);
