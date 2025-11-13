document.addEventListener('DOMContentLoaded', () => {
  // select all toggle
  const selectAll = document.getElementById('select-all');
  if (selectAll) {
    selectAll.addEventListener('change', () => {
      const checked = selectAll.checked;
      document.querySelectorAll('.row-select').forEach(cb => cb.checked = checked);
    });
  }

  // confirm forms that have data-confirm attribute
  document.querySelectorAll('form[data-confirm="true"]').forEach(form => {
    form.addEventListener('submit', (e) => {
      const msg = form.getAttribute('data-confirm-message') || 'Deseja prosseguir?';
      if (!confirm(msg)) {
        e.preventDefault();
      }
    });
  });
});
