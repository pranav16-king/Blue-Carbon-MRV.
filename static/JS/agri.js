// Header sticky and sidenav logic
const header = document.getElementById('header-a');
let stickyAdded = false;
window.addEventListener('scroll', () => {
  if (window.scrollY > 40 && header) {
    if (!stickyAdded) {
      header.classList.add('header-sticky-a');
      stickyAdded = true;
    }
    document.getElementById('sidenav-a').classList.add('sidenav-active-a');
    header.style.opacity = "0";
  } else {
    if (stickyAdded && header) {
      header.classList.remove('header-sticky-a');
      stickyAdded = false;
    }
    document.getElementById('sidenav-a').classList.remove('sidenav-active-a');
    header.style.opacity = "1";
  }
});
const sidenav = document.getElementById('sidenav-a');
sidenav.classList.remove('sidenav-active-a');