
function randomData(num) {
    return Array.from({ length: num }, () => Math.floor(Math.random() * 200) + 50);
}

const projectCtx = document.getElementById('projectChart').getContext('2d');
const projectChart = new Chart(projectCtx, {
    type: 'line',
    data: {
        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'],
        datasets: [{
            label: 'Projects Approved',
            data: randomData(7),
            backgroundColor: 'rgba(59, 130, 246,0.2)',
            borderColor: 'rgba(59, 130, 246,1)',
            borderWidth: 2,
            fill: true,
            tension: 0.3
        }]
    },
    options: {
        responsive: true,
        plugins: { legend: { display: true } },
        scales: { y: { beginAtZero: true } }
    }
});

const creditCtx = document.getElementById('creditChart').getContext('2d');
const creditChart = new Chart(creditCtx, {
    type: 'bar',
    data: {
        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'],
        datasets: [{
            label: 'Carbon Credits Issued',
            data: randomData(7),
            backgroundColor: 'rgba(34,197,94,0.7)',
            borderColor: 'rgba(21,128,61,1)',
            borderWidth: 1
        }]
    },
    options: {
        responsive: true,
        plugins: { legend: { display: true } },
        scales: { y: { beginAtZero: true } }
    }
});
