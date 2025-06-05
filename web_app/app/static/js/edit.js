let questionIndex;

document.addEventListener("DOMContentLoaded", function () {
    console.log("DOM Content Loaded");
    
    const container = document.getElementById('edit-survey-container');
    if (!container) {
        console.error("Container not found!");
        return;
    }
    
    // Получаем количество существующих вопросов
    const existingQuestions = container.querySelectorAll('.question-block');
    questionIndex = existingQuestions.length;
    console.log("Number of existing questions:", questionIndex);
    console.log("Initial question index:", questionIndex);

    // Предотвращаем отправку формы при нажатии на кнопки
    const form = document.getElementById('edit-survey-form');
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            console.log("Form submission intercepted");
            
            // Проверяем, что есть хотя бы один вопрос
            const questions = document.querySelectorAll('.question-block');
            if (questions.length === 0) {
                const alert = document.getElementById('form-alert');
                alert.classList.remove('d-none');
                return;
            }

            // Обновляем индексы перед отправкой
            updateExistingQuestionIndices();
            
            // Проверяем, что все вопросы имеют ответы (кроме текстовых)
            let isValid = true;
            questions.forEach((question, index) => {
                const type = question.querySelector('select').value;
                const answers = question.querySelectorAll('.answer-row');
                if (type !== 'text' && answers.length === 0) {
                    isValid = false;
                    console.error(`Question ${index} has no answers`);
                }
            });

            if (!isValid) {
                alert('Пожалуйста, добавьте хотя бы один ответ для каждого вопроса');
                return;
            }

            // Отправляем форму
            console.log("Submitting form...");
            form.submit();
        });
    }

    // Используем делегирование событий для всех кнопок
    container.addEventListener('click', function(e) {
        const target = e.target;

        // Добавление вопроса
        if (target.id === 'add-question-btn') {
            e.preventDefault();
            console.log("Add question button clicked");
            addQuestion();
        }

        // Добавление ответа
        if (target.classList.contains('btn-add-answer')) {
            e.preventDefault();
            console.log("Add answer button clicked");
            const questionBlock = target.closest('.question-block');
            const questionIndex = questionBlock.querySelector('select').dataset.questionIndex;
            addAnswer(target, questionIndex);
        }

        // Удаление вопроса
        if (target.classList.contains('remove-question')) {
            e.preventDefault();
            console.log("Remove question button clicked");
            removeQuestion(target);
        }

        // Удаление ответа
        if (target.classList.contains('remove-answer')) {
            e.preventDefault();
            console.log("Remove answer button clicked");
            target.closest('.answer-row').remove();
        }

        // Удаление изображения
        if (target.classList.contains('remove-image')) {
            e.preventDefault();
            console.log("Remove image button clicked");
            removeImage(target);
        }
    });

    // Обработчик изменения типа вопроса
    container.addEventListener('change', function(e) {
        if (e.target.tagName === 'SELECT' && e.target.name.includes('[type]')) {
            console.log("Question type changed");
            onQuestionTypeChange(e.target);
        }
    });

    // Обработчик загрузки изображения
    container.addEventListener('change', function(e) {
        if (e.target.classList.contains('question-image-input')) {
            console.log("Image input changed");
            previewImage(e.target);
        }
    });

    // Проверяем и обновляем индексы существующих вопросов
    updateExistingQuestionIndices();
});

function updateExistingQuestionIndices() {
    console.log("Updating question indices");
    const questions = document.querySelectorAll('.question-block');
    questions.forEach((question, index) => {
        console.log(`Updating question ${index}`);
        // Обновляем все поля вопроса
        question.querySelectorAll('[name]').forEach(input => {
            const name = input.name;
            if (name.includes('questions[')) {
                const newName = name.replace(/questions\[\d+\]/, `questions[${index}]`);
                input.name = newName;
                console.log(`Updated name: ${name} -> ${newName}`);
            }
        });

        // Обновляем data-question-index для select
        const select = question.querySelector('select');
        if (select) {
            select.setAttribute('data-question-index', index);
            console.log(`Updated select data-question-index to ${index}`);
        }
    });
}

function addQuestion() {
    console.log("Adding new question");
    const container = document.getElementById('questions-container');
    if (!container) {
        console.error("Questions container not found!");
        return;
    }

    const template = document.getElementById('question-template');
    if (!template) {
        console.error("Question template not found!");
        return;
    }

    const questionNode = template.content.cloneNode(true);
    console.log("Template cloned");

    // Обновляем индексы в name атрибутах
    questionNode.querySelectorAll('[name]').forEach(input => {
        const name = input.name;
        if (name.includes('questions[]')) {
            input.name = name.replace('questions[]', `questions[${questionIndex}]`);
            console.log(`Updated name: ${name} -> ${input.name}`);
        }
    });

    // Обновляем data-question-index для select
    const select = questionNode.querySelector('select');
    select.setAttribute('data-question-index', questionIndex);
    console.log(`Set select data-question-index to ${questionIndex}`);

    container.appendChild(questionNode);
    console.log("New question added, index:", questionIndex);
    questionIndex++;
}

function addAnswer(button, questionIndex) {
    console.log("Adding new answer for question", questionIndex);
    const answersContainer = button.previousElementSibling;
    if (!answersContainer) {
        console.error("Answers container not found!");
        return;
    }

    const template = document.getElementById('answer-template');
    if (!template) {
        console.error("Answer template not found!");
        return;
    }

    const answerNode = template.content.cloneNode(true);
    console.log("Answer template cloned");

    // Обновляем индекс в name атрибуте
    answerNode.querySelectorAll('input[name]').forEach(input => {
        const name = input.name;
        if (name.includes('questions[]')) {
            input.name = name.replace('questions[]', `questions[${questionIndex}]`);
            console.log(`Updated answer name: ${name} -> ${input.name}`);
        }
    });

    answersContainer.appendChild(answerNode);
    console.log("New answer added");
}

function removeQuestion(button) {
    button.closest('.question-block').remove();
    // После удаления вопроса обновляем индексы
    updateExistingQuestionIndices();
}

function onQuestionTypeChange(select) {
    const questionBlock = select.closest('.question-block');
    const answersContainer = questionBlock.querySelector('.answers-container');
    const addAnswerButton = questionBlock.querySelector('.btn-add-answer');
    const type = select.value;

    if (type === 'text') {
        answersContainer.innerHTML = '';
        addAnswerButton.style.display = 'none';
    } else {
        if (answersContainer.children.length === 0) {
            addAnswer(addAnswerButton, select.dataset.questionIndex);
        }
        addAnswerButton.style.display = 'block';
        const radioInputs = answersContainer.querySelectorAll('input[type="radio"]');
        radioInputs.forEach(input => {
            input.type = type === 'multiple' ? 'checkbox' : 'radio';
        });
    }
}

function previewImage(input) {
    const container = input.closest('.col-md-4').querySelector('.image-preview-container');
    const img = container.querySelector('.img-preview');
    
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function(e) {
            img.src = e.target.result;
            container.classList.remove('d-none');
        }
        reader.readAsDataURL(input.files[0]);
    }
}

function removeImage(button) {
    const container = button.closest('.image-preview-container');
    const input = container.previousElementSibling.querySelector('input[type="file"]');
    input.value = '';
    container.classList.add('d-none');
    container.querySelector('.img-preview').src = '';
}