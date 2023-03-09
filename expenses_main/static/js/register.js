const usernameField = document.querySelector('#usernameField');
const emailField = document.querySelector('#emailField');
const passwordField = document.querySelector('#passwordField');
const userFeedbackArea = document.querySelector('.username_feedback');
const emailFeedbackArea = document.querySelector('.email_feedback');
const usernameCheck = document.querySelector('.username_check');
const emailCheck = document.querySelector('.email_check');
const showPasswordToggle = document.querySelector('.showPasswordToggle');
const submitBtn = document.querySelector('.submit-btn');


const handleToggleInput = (e) => {
    if (showPasswordToggle.textContent === 'SHOW') {
        showPasswordToggle.textContent = 'HIDE';
        passwordField.setAttribute("type", "text");
    } else {
        showPasswordToggle.textContent = 'SHOW';
        passwordField.setAttribute("type", "password");
    }
};

showPasswordToggle.addEventListener('click', handleToggleInput);

//emailField.addEventListener('input', (e) => {
//    if (emailField.value.length === 0) {
//        emailFeedbackArea.style.display = 'none';
//        emailField.classList.remove('is-invalid');
//    }
//});

emailField.addEventListener('keyup', (e) => {
    const emailValue = e.target.value;
    emailCheck.style.display = 'block';
    emailCheck.textContent = `Checking ${emailValue}..`;
    if (emailValue.length > 0) {
        fetch('/authentication/validate-email/', {
            body: JSON.stringify({ email: emailValue }),
            method: 'POST'
        }).then(res => res.json())
            .then(data => {
                emailCheck.style.display = 'none';
                if (data.email_error) {
                    submitBtn.disabled = true;
                    emailField.classList.add('is-invalid');
                    emailFeedbackArea.style.display = 'block';
                    emailFeedbackArea.innerHTML = `<p>${data.email_error}</p>`;
                } else {
                    submitBtn.removeAttribute('disabled');
                    emailFeedbackArea.style.display = 'none';
                    emailField.classList.remove('is-invalid');
                }
            });
    } else {
        emailCheck.style.display = 'none';
        emailFeedbackArea.style.display = 'none';
        emailField.classList.remove('is-invalid');
    }
});

usernameField.addEventListener('keyup', (e) => {
    const usernameValue = e.target.value;
    usernameCheck.style.display = 'block';
    usernameCheck.textContent = `Checking ${usernameValue}..`;
    if (usernameValue.length > 0) {
        fetch('/authentication/validate-username/', {
            body: JSON.stringify({ username: usernameValue }),
            method: 'POST'
        }).then(res => res.json())
            .then(data => {
                usernameCheck.style.display = 'none';
                if (data.username_error) {
                    submitBtn.disabled = true;
                    usernameField.classList.add('is-invalid');
                    userFeedbackArea.style.display = 'block';
                    userFeedbackArea.innerHTML = `<p>${data.username_error}</p>`;
                } else {
                    submitBtn.removeAttribute('disabled');
                    usernameField.classList.remove('is-invalid');
                    userFeedbackArea.style.display = 'none';
                }
            });
    } else {
        usernameCheck.style.display = 'none';
        usernameField.classList.remove('is-invalid');
        userFeedbackArea.style.display = 'none';
    }
});