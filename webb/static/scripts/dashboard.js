const balanceDisplay = document.getElementById("balance");
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
    `;
    tableBody.appendChild(newRow);
  });
}

// Muat data saat halaman selesai dimuat
document.addEventListener("DOMContentLoaded", () => {
  loadTasks();
  loadBalance();
});

// Function to format currency
function formatCurrency(amount) {
  return new Intl.NumberFormat("id-ID", {
    style: "currency",
    currency: "IDR",
  }).format(amount);
}

function loadBalance() {
  let allTransactions = [];
  for (let index = 0; index < 12; index++) {
    const key = `transactions_${index + 1}`;
    const transactions = localStorage.getItem(key);
    const transactionsArray = transactions ? JSON.parse(transactions) : [];
    const balance =
      transactionsArray !== null && transactionsArray.length > 0
        ? transactionsArray[transactionsArray.length - 1].balance
        : 0;
    allTransactions.push(balance);
  }
  let balance = 0;
  allTransactions.forEach((element) => {
    balance = balance + element;
  });
  balanceDisplay.textContent = `Saldo: ${formatCurrency(balance)}`;
}
