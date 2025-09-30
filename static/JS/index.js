const tabButtons = document.querySelectorAll('.tab-btn-b');
const tabs = document.querySelectorAll('.tab-b');
tabButtons.forEach(btn => {
    btn.addEventListener('click', () => {
        tabButtons.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const target = btn.dataset.tab;
        tabs.forEach(t => t.style.display = (t.id === target ? 'block' : 'none'));
    });
});

const ctx = document.getElementById('priceChart').getContext('2d');
const labels = Array.from({ length: 60 }, (_, i) => `${i - 59}s`);
let last = 950;
function stableJitter() {
    const mean = 950;
    const drift = (mean - last) * 0.1;
    last += drift + (Math.random() - 0.5) * 0.6;
    if (last < 945) last = 945;
    if (last > 955) last = 955;
    return Number(last.toFixed(2));
}
const data = Array.from({ length: labels.length }, stableJitter);
const chart = new Chart(ctx, {
    type: 'line',
    data: { labels, datasets: [{ data, borderWidth: 2, fill: true, tension: 0.15, borderColor: 'rgba(59,130,246,1)', backgroundColor: 'rgba(96,165,250,0.2)', pointRadius: 0 }] },
    options: { responsive: true, maintainAspectRatio: false, animation: false, scales: { y: { min: 945, max: 955 } }, plugins: { legend: { display: false } } }
});
setInterval(() => {
    chart.data.labels.push('now'); chart.data.labels.shift();
    chart.data.datasets[0].data.push(stableJitter()); chart.data.datasets[0].data.shift();
    chart.update('none');
}, 1000);

const asksBody = document.getElementById('asksBody');
const recentTrades = document.getElementById('recentTrades');
function randomInt(min, max) { return Math.floor(Math.random() * (max - min + 1)) + min; }
function seedOrders() {
    asksBody.innerHTML = ''; recentTrades.innerHTML = '';
    const mid = 950 + Math.random() * 5;
    for (let i = 0; i < 10; i++) {
        const pAsk = (mid + i * 0.5 + Math.random()).toFixed(2);
        const qAsk = randomInt(10, 300);
        const trA = document.createElement('tr');
        trA.innerHTML = `<td>₹ ${pAsk}</td><td>${qAsk}</td><td>₹ ${(pAsk * qAsk).toFixed(2)}</td>`;
        asksBody.appendChild(trA);

        const pTrade = (mid + (Math.random() - 0.5) * 2).toFixed(2);
        const qTrade = randomInt(5, 100);
        const trT = document.createElement('tr');
        const time = new Date().toLocaleTimeString();
        trT.innerHTML = `<td>₹ ${pTrade}</td><td>${qTrade}</td><td>${time}</td>`;
        recentTrades.appendChild(trT);
    }
}
seedOrders();
setInterval(seedOrders, 5000);

const newsData = [
    { img: '/static/news_imges/news1.jpg', title: 'New Carbon Project Launched', desc: 'A new mangrove project approved for carbon credits.' },
    { img: '/static/news_imges/news2.jpeg', title: 'Market Update', desc: 'Carbon credit prices show steady growth this week.' },
    { img: '/static/news_imges/news3.webp', title: 'Policy News', desc: 'Government announces incentives for carbon trading.' }
];
const newsSection = document.getElementById('newsSection');
newsData.forEach(n => {
    const div = document.createElement('div');
    div.className = 'news-item';
    div.innerHTML = `<img src='${n.img}' alt='${n.title}' /><div class='news-content'><div class='news-title'>${n.title}</div><div class='news-desc'>${n.desc}</div></div>`;
    newsSection.appendChild(div);
});
// Simple blockchain simulation
document.addEventListener('DOMContentLoaded', function () {
    // Connect wallet functionality
    const connectWalletBtn = document.querySelector('button:contains("Connect Wallet")');
    if (connectWalletBtn) {
        connectWalletBtn.addEventListener('click', function () {
            this.innerHTML = '<i class="fas fa-check-circle mr-2"></i>Wallet Connected';
            this.classList.remove('bg-white');
            this.classList.add('bg-green-500');

            // Show notification
            showNotification('Wallet connected successfully!', 'success');
        });
    }

    // Upload form handling
    const uploadForm = document.querySelector('form');
    if (uploadForm) {
        uploadForm.addEventListener('submit', function (e) {
            e.preventDefault();
            showNotification('Data uploaded to blockchain successfully!', 'success');
            this.reset();
        });
    }

    // Notification function
    function showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg text-white ${type === 'success' ? 'bg-green-500' :
            type === 'error' ? 'bg-red-500' : 'bg-blue-500'
            }`;
        notification.innerHTML = `
                    <div class="flex items-center">
                        <i class="fas fa-${type === 'success' ? 'check-circle' : 'info-circle'} mr-2"></i>
                        ${message}
                    </div>
                `;
        document.body.appendChild(notification);

        setTimeout(() => {
            notification.remove();
        }, 3000);
    }

    // Smooth scrolling for navigation
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
});
