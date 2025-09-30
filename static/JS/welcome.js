
// Create particles
function createParticles() {
    const particlesContainer = document.getElementById('particles');
    const particleCount = 50;

    for (let i = 0; i < particleCount; i++) {
        const particle = document.createElement('div');
        particle.classList.add('particle');

        // Random properties
        const size = Math.random() * 15 + 5;
        const left = Math.random() * 100;
        const duration = Math.random() * 20 + 10;
        const delay = Math.random() * 5;

        particle.style.width = `${size}px`;
        particle.style.height = `${size}px`;
        particle.style.left = `${left}%`;
        particle.style.animationDuration = `${duration}s`;
        particle.style.animationDelay = `${delay}s`;

        particlesContainer.appendChild(particle);
    }
}

// Add animation classes with delays
function addAnimationDelays() {
    const elements = document.querySelectorAll('.animate-float, .animate-slideInFromTop, .animate-slideInFromBottom, .animate-fadeIn, .animate-glow');
    elements.forEach((el, index) => {
        el.style.animationDelay = `${index * 0.2}s`;
    });
}

// Initialize everything
document.addEventListener('DOMContentLoaded', () => {
    createParticles();
    addAnimationDelays();

    // Add hover effects
    const buttons = document.querySelectorAll('button');
    buttons.forEach(button => {
        button.addEventListener('mouseenter', () => {
            button.style.transform = 'scale(1.1) rotate(2deg)';
        });
        button.addEventListener('mouseleave', () => {
            button.style.transform = 'scale(1) rotate(0deg)';
        });
    });
});
