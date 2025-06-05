document.getElementById('surveyForm').addEventListener('submit', function(e) {
    const requiredQuestions = document.querySelectorAll('[required]');
    let isValid = true;

    requiredQuestions.forEach(input => {
        if (input.type === 'checkbox') {
            const name = input.name;
            const checkboxes = document.querySelectorAll(`input[name="${name}"]`);
            const checked = Array.from(checkboxes).some(cb => cb.checked);
            
            if (!checked) {
                isValid = false;
                input.closest('.mb-4').classList.add('border', 'border-danger', 'p-3', 'rounded');
            } else {
                input.closest('.mb-4').classList.remove('border', 'border-danger', 'p-3', 'rounded');
            }
        } else {
            if (!input.value.trim()) {
                isValid = false;
                input.closest('.mb-4').classList.add('border', 'border-danger', 'p-3', 'rounded');
            } else {
                input.closest('.mb-4').classList.remove('border', 'border-danger', 'p-3', 'rounded');
            }
        }
    });

    if (!isValid) {
        e.preventDefault();
        alert('Пожалуйста, ответьте на все обязательные вопросы');
    }
});