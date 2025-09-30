
const refreshBtn = document.getElementById('refreshBtn');
if (refreshBtn) refreshBtn.addEventListener('click', () => window.location.reload());

async function act(id, action) {
    try {
        const res = await fetch("/action", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ id, action })
        });
        const data = await res.json();
        if (!res.ok || !data.ok) throw new Error(data.error || "Action failed");

        if (action === "reject") {
            const el = document.getElementById(`card-${id}`);
            if (el) {
                el.classList.add("animate__animated", "animate__fadeOut", "animate__faster");
                setTimeout(() => el.remove(), 500);
            }
        } else if (action === "accept") {
            const card = document.getElementById(`card-${id}`);
            if (card) {
                const statusBadge = card.querySelector("div.absolute.top-2.right-2");
                if (statusBadge) statusBadge.textContent = "Accepted";
                const btn = card.querySelector("button[onclick*=\"'accept'\"]");
                if (btn) btn.disabled = true;
                const burst = document.createElement("div");
                burst.className = "fixed inset-0 pointer-events-none animate__animated animate__fadeOut";
                burst.innerHTML = `<div class="absolute inset-0 bg-sky-200/40"></div>`;
                document.body.appendChild(burst);
                setTimeout(() => burst.remove(), 600);
            }
        }
    } catch (e) {
        alert(e.message || e.toString());
    }
}
