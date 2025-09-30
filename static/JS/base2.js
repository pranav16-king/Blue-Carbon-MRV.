const toggleBtn = document.getElementById('toggleSidebar');
const sidebar = document.getElementById('sidebar');
const mainContent = document.getElementById('mainContent');

toggleBtn.addEventListener('click', () => {
    sidebar.classList.toggle('collapsed');
    if (sidebar.classList.contains('collapsed')) {
        mainContent.classList.remove('ml-[240px]');
        mainContent.classList.add('ml-[72px]');
    } else {
        mainContent.classList.remove('ml-[72px]');
        mainContent.classList.add('ml-[240px]');
    }
});
