const MAX_CHECKLIST = 18;

// Function to load tasks from local storage or backend
async function loadTasks() {
  const tasks = JSON.parse(localStorage.getItem("tasks")) || [];

  // If local storage is empty, fetch from backend
  if (tasks.length === 0) {
    const response = await fetch('/dashboard/courses/get_tasks');
    const fetchedTasks = await response.json();
    localStorage.setItem("tasks", JSON.stringify(fetchedTasks));
    renderTasks(fetchedTasks);
  } else {
    renderTasks(tasks);
  }
}

// Function to render tasks to the table
function renderTasks(tasks) {
  const tableBody = document.getElementById("taskTableBody");
  tableBody.innerHTML = ""; // Clear table before rendering

  tasks.forEach((task) => {
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
      <td><button class="delete-button" data-name="${task.name}">Hapus</button></td>
    `;
    tableBody.appendChild(newRow);
  });

  // Add event listeners for checkboxes
  document.querySelectorAll(".task-checkbox").forEach((checkbox) => {
    checkbox.addEventListener("change", updateChecklist);
  });
}

// Function to update checklist counts
function updateChecklist() {
  const checkboxes = document.querySelectorAll(".task-checkbox");
  let checkedCount = 0;

  checkboxes.forEach((checkbox) => {
    if (checkbox.checked) {
      checkedCount++;
    }
  });

  checkboxes.forEach((checkbox) => {
    const checkCountSpan = checkbox.nextElementSibling;
    checkCountSpan.textContent = `${checkedCount}/${MAX_CHECKLIST}`;
  });
}

// Function to handle form submission and add task
async function addTask(event) {
  event.preventDefault();

  const taskName = document.getElementById("taskName").value;
  const taskDeadline = document.getElementById("taskDeadline").value;
  const taskSource = document.getElementById("taskSource").value;
  const taskLink = document.getElementById("taskLink").value;

  const newTask = { name: taskName, deadline: taskDeadline, source: taskSource, link: taskLink };

  // Save to backend
  await fetch('/dashboard/courses/add_task', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(newTask),
  });

  // Update local storage
  const tasks = JSON.parse(localStorage.getItem("tasks")) || [];
  tasks.push(newTask);
  localStorage.setItem("tasks", JSON.stringify(tasks));

  renderTasks(tasks);
  document.getElementById("taskForm").reset();
}

// Function to handle task deletion
async function deleteTask(event) {
  if (event.target.classList.contains("delete-button")) {
    const taskName = event.target.getAttribute("data-name");

    // Delete from backend
    await fetch('/dashboard/courses/delete_task', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: taskName }),
    });

    // Update local storage
    const tasks = JSON.parse(localStorage.getItem("tasks")) || [];
    const updatedTasks = tasks.filter((task) => task.name !== taskName);
    localStorage.setItem("tasks", JSON.stringify(updatedTasks));

    renderTasks(updatedTasks);
  }
}

// Event listener for form submission
document.getElementById("taskForm").addEventListener("submit", addTask);

// Event listener for delete button
document.getElementById("taskTableBody").addEventListener("click", deleteTask);

// Load tasks on page load
document.addEventListener("DOMContentLoaded", loadTasks);
