// Tailwind on CDN: extend a soft sky palette
tailwind.config = {
    theme: {
        extend: {
            colors: {
                skyink: {
                    50: '#f0f9ff',
                    100: '#e0f2fe',
                    200: '#bae6fd',
                    300: '#7dd3fc',
                    400: '#38bdf8',
                    500: '#0ea5e9',
                    600: '#0284c7',
                    700: '#0369a1',
                    800: '#075985',
                    900: '#0c4a6e'
                }
            },
            boxShadow: {
                soft: '0 10px 25px -5px rgba(14,165,233,0.25), 0 8px 10px -6px rgba(14,165,233,0.15)'
            }
        }
    }
}
const grid = document.getElementById('newsGrid');
const cards = Array.from(document.querySelectorAll('.card'));
const tabs = Array.from(document.querySelectorAll('[data-filter]'));
const tags = Array.from(document.querySelectorAll('.tag'));
const searchInput = document.getElementById('search');
const clearBtn = document.getElementById('clearSearch');

function applyFilters(filter = 'all', query = '') {
    const q = query.trim().toLowerCase();
    cards.forEach(card => {
        const tags = (card.getAttribute('data-tags') || '').toLowerCase();
        const text = card.textContent.toLowerCase();
        const matchesTag = filter === 'all' || tags.includes(filter);
        const matchesQuery = !q || text.includes(q);
        card.classList.toggle('hidden', !(matchesTag && matchesQuery));
    });
}

tabs.forEach(tab => tab.addEventListener('click', e => {
    e.preventDefault();
    const filter = tab.getAttribute('data-filter');
    applyFilters(filter, searchInput ? searchInput.value : '');
}));

tags.forEach(tag => tag.addEventListener('click', () => {
    const filter = tag.getAttribute('data-filter');
    applyFilters(filter, searchInput ? searchInput.value : '');
}));

if (searchInput) {
    searchInput.addEventListener('input', () => applyFilters('all', searchInput.value));
}

if (clearBtn) {
    clearBtn.addEventListener('click', () => {
        searchInput.value = '';
        applyFilters('all', '');
    });
}

// Mobile menu toggle
const menuBtn = document.getElementById('menuBtn');
const mobileNav = document.getElementById('mobileNav');
if (menuBtn && mobileNav) {
    menuBtn.addEventListener('click', () => mobileNav.classList.toggle('hidden'));
}
