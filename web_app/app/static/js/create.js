let questionIndex = 0;

function addQuestion() {
    const container = document.getElementById('questions-container');
    const template = document.getElementById('question-template');
    const questionNode = template.content.cloneNode(true);

    questionNode.querySelectorAll('[name]').forEach(input => {
        input.name = input.name.replace('questions[][', `questions[${questionIndex}][`);
    });

    container.appendChild(questionNode);

    const lastQuestion = container.lastElementChild;
    const select = lastQuestion.querySelector('select');
    select.setAttribute('data-question-index', questionIndex);

    addAnswer(lastQuestion.querySelector('.btn-add-answer'), questionIndex);
    onQuestionTypeChange(select);

    questionIndex++;
}


function addAnswer(button, questionIdx = null) {
    const cardBody = button.closest('.card-body');
    const answersContainer = cardBody.querySelector('.answers-container');
    const answerTemplate = document.getElementById('answer-template').content.cloneNode(true);

    const select = cardBody.querySelector('select');
    const qIndex = questionIdx !== null ? questionIdx : select.dataset.questionIndex;

    const input = answerTemplate.querySelector('input');
    input.name = `questions[${qIndex}][answers][]`;

    answersContainer.appendChild(answerTemplate);
    updateAnswerIcons(answersContainer, select.value);
}


function removeQuestion(button) {
    button.closest('.question-block').remove();
}

function onQuestionTypeChange(select) {
    const cardBody = select.closest('.card-body');
    const answersContainer = cardBody.querySelector('.answers-container');
    const addAnswerBtn = cardBody.querySelector('.btn-add-answer');

    if (select.value === 'text') {

        answersContainer.style.display = 'none';
        addAnswerBtn.style.display = 'none';
        answersContainer.innerHTML = '';  
    } else {
        answersContainer.style.display = '';
        addAnswerBtn.style.display = '';
        if (answersContainer.children.length === 0) {
            addAnswer(addAnswerBtn);
        }
        updateAnswerIcons(answersContainer, select.value);
    }
}


function updateAnswerIcons(container, type) {
    const iconSpans = container.querySelectorAll('.input-type-icon');
    iconSpans.forEach((span, i) => {
        if (type === 'single') {
            span.innerHTML = `<input type="radio" disabled>`;
        } else if (type === 'multiple') {
            span.innerHTML = `<input type="checkbox" disabled>`;
        } else {
            span.innerHTML = '';
        }
    });
}

function previewImage(input) {
    const container = input.closest('.card-body');
    const previewContainer = container.querySelector('.image-preview-container');
    const preview = previewContainer.querySelector('.img-preview');
    
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        
        reader.onload = function(e) {
            preview.src = e.target.result;
            previewContainer.classList.remove('d-none');
        }
        
        reader.readAsDataURL(input.files[0]);
    }
}

function removeImage(button) {
    const container = button.closest('.card-body');
    const previewContainer = container.querySelector('.image-preview-container');
    const fileInput = container.querySelector('.question-image-input');
    
    previewContainer.classList.add('d-none');
    previewContainer.querySelector('.img-preview').src = '';
    fileInput.value = '';
}

const form = document.querySelector('form');
const startInput = document.getElementById('start_date');
const endInput = document.getElementById('end_date');

function toUtcISOString(localDateStr) {
    if (!localDateStr) return '';
    const localDate = new Date(localDateStr);
    return localDate.toISOString().slice(0,16);
}

form.addEventListener('submit', (e) => {
    const questionsContainer = document.getElementById('questions-container');
    const alertBox = document.getElementById('form-alert');

    if (questionsContainer.children.length === 0) {
        e.preventDefault(); 
        alertBox.classList.remove('d-none');
        return;
    }

    alertBox.classList.add('d-none');

    if (startInput.value) {
        startInput.value = toUtcISOString(startInput.value);
    }
    if (endInput.value) {
        endInput.value = toUtcISOString(endInput.value);
    }
});