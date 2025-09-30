
function loadProjects() {
  const projectList = document.getElementById("projectList");
  const projectCount = document.getElementById("projectCount");
  projectList.innerHTML = "";

  const projects = JSON.parse(localStorage.getItem("projects")) || [];
  projectCount.textContent = projects.length;

  if (projects.length === 0) {
    projectList.innerHTML = `<p class="text-center text-gray-500 col-span-3">No pending projects yet.</p>`;
    return;
  }

  projects.forEach((p, index) => {
    const card = document.createElement("div");
    card.className = "bg-white rounded-2xl overflow-hidden shadow-lg hover:shadow-2xl transition";

    card.innerHTML = `
          <img src="${p.image}" class="h-48 w-full object-cover">
          <div class="p-6">
            <h3 class="text-xl font-bold mb-2">${p.name}</h3>
            <p class="text-gray-600 mb-2">${p.description}</p>
            <p class="text-gray-500 text-sm"><i class="fas fa-map-marker-alt text-red-500"></i> ${p.location}</p>
            <p class="text-gray-500 text-sm">📍 Coordinates: ${p.latitude.toFixed(5)}, ${p.longitude.toFixed(5)}</p>
            <div class="flex justify-between items-center mt-4">
              <button onclick="acceptProject(${index})" class="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition">
                Accept
              </button>
              <button onclick="rejectProject(${index})" class="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition">
                Reject
              </button>
            </div>
          </div>
        `;
    projectList.appendChild(card);
  });
}

function acceptProject(index) {
  alert("Project accepted ✅");
  removeProject(index);
}

function rejectProject(index) {
  alert("Project rejected ❌");
  removeProject(index);
}

function removeProject(index) {
  let projects = JSON.parse(localStorage.getItem("projects")) || [];
  projects.splice(index, 1);
  localStorage.setItem("projects", JSON.stringify(projects));
  loadProjects();
}

window.onload = loadProjects;

