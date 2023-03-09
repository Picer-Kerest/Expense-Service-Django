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


