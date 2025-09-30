const container = document.querySelector('.container');
const registerBtn = document.querySelector('.register-btn');
const LoginBtn = document.querySelector('.login-btn');

registerBtn.addEventListener('click', () => {
    container.classList.add('active');
})
LoginBtn.addEventListener('click', () => {
    container.classList.remove('active');
})
