const MAX_CHECKLIST = 18;

// Fungsi untuk memuat data dari localStorage
function loadTasks() {
  const tasks = JSON.parse(localStorage.getItem("tasks")) || [];
  const tableBody = document.getElementById("taskTableBody");
  tableBody.innerHTML = ""; // Kosongkan tabel sebelum memuat data

  tasks.forEach((task, index) => {
    const newRow = document.createElement("tr");
    newRow.innerHTML = `
      <td>
        <input type="checkbox" class="task-checkbox">
        <span class="check-count">0/${MAX_CHECKLIST}</span>
      </td>
      <td>${task.name}</td>
      <td>${new Date(task.deadline).toLocaleString()}</td>
      <td><a href="${task.source}" target="_blank">Lihat Materi</a></td>
      <td><a href="${task.link}" target="_blank">Kumpulkan</a></td>
      <td><button class="delete-button" data-index="${index}">Hapus</button></td>
    `;
    tableBody.appendChild(newRow);
  });

  // Tambahkan event listener ke semua checkbox
  document.querySelectorAll(".task-checkbox").forEach((checkbox) => {
    checkbox.addEventListener("change", updateChecklist);
  });
}

// Fungsi untuk menyimpan data ke localStorage
function saveTasks() {
  const tasks = [];
  const tableRows = document.querySelectorAll("#taskTableBody tr");

  tableRows.forEach((row) => {
    const name = row.cells[1].textContent;
    const deadline = new Date(row.cells[2].textContent).toISOString();
    const source = row.cells[3].querySelector("a").href;
    const link = row.cells[4].querySelector("a").href;
    tasks.push({ name, deadline, source, link });
  });

  localStorage.setItem("tasks", JSON.stringify(tasks));
}

// Fungsi untuk memperbarui jumlah checklist
function updateChecklist() {
  const checkboxes = document.querySelectorAll(".task-checkbox");
  let checkedCount = 0;

  checkboxes.forEach((checkbox) => {
    if (checkbox.checked) {
      checkedCount++;
    }
  });

  // Perbarui tampilan setiap count checklist
  checkboxes.forEach((checkbox) => {
    const checkCountSpan = checkbox.nextElementSibling;
    checkCountSpan.textContent = `${checkedCount}/${MAX_CHECKLIST}`;
  });
}

// Event listener untuk form submission
document
  .getElementById("taskForm")
  .addEventListener("submit", function (event) {
    event.preventDefault();

    const taskName = document.getElementById("taskName").value;
    const taskDeadline = document.getElementById("taskDeadline").value;
    const taskSource = document.getElementById("taskSource").value;
    const taskLink = document.getElementById("taskLink").value;

    const tableBody = document.getElementById("taskTableBody");
    const newRow = document.createElement("tr");
    newRow.innerHTML = `
    <td>
      <input type="checkbox" class="task-checkbox">
      <span class="check-count">0/${MAX_CHECKLIST}</span>
    </td>
    <td>${taskName}</td>
    <td>${new Date(taskDeadline).toLocaleString()}</td>
    <td><a href="${taskSource}" target="_blank">Lihat Materi</a></td>
    <td><a href="${taskLink}" target="_blank">Kumpulkan</a></td>
    <td><button class="delete-button">Hapus</button></td>
  `;
    tableBody.appendChild(newRow);

    saveTasks(); // Simpan data ke localStorage
    document.getElementById("taskForm").reset();
  });

// Event listener untuk tombol delete
document
  .getElementById("taskTableBody")
  .addEventListener("click", function (event) {
    if (event.target.classList.contains("delete-button")) {
      const row = event.target.closest("tr");
      row.remove(); // Hapus baris dari tabel
      saveTasks(); // Simpan perubahan ke localStorage
    }
  });

// Muat data saat halaman selesai dimuat
document.addEventListener("DOMContentLoaded", loadTasks);
