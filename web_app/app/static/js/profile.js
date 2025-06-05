const editBtn = document.getElementById('edit-btn');
const saveBtn = document.getElementById('save-btn');
const form = document.getElementById('profile-form');

editBtn.addEventListener('click', () => {
    const inputs = form.querySelectorAll('input');
    const selects = form.querySelectorAll('select');

    inputs.forEach(input => {
        if (input.name !== 'username' && input.type !== 'email') {
            input.removeAttribute('disabled');
        }
    });


    selects.forEach(select => select.removeAttribute('disabled'));

    editBtn.classList.add('d-none');
    saveBtn.classList.remove('d-none');
});