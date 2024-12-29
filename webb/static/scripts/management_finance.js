// Load jsPDF for PDF generation
const script = document.createElement("script");
script.src =
  "https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js";
document.head.appendChild(script);

// Get required elements
const form = document.getElementById("transaction-form");
const tableBody = document.querySelector("#finance-table tbody");
const downloadPdfBtn = document.getElementById("download-pdf");
const balanceDisplay = document.getElementById("balance");
const monthSelect = document.getElementById("month");

// Initialize running balance
let currentBalance = 0;

// Get current month for initial load
const currentDate = new Date();
monthSelect.value = (currentDate.getMonth() + 1).toString();

// Function to format currency
function formatCurrency(amount) {
  return new Intl.NumberFormat("id-ID", {
    style: "currency",
    currency: "IDR",
  }).format(amount);
}

// Function to get month name
function getMonthName(monthNumber) {
  const months = [
    "Januari",
    "Februari",
    "Maret",
    "April",
    "Mei",
    "Juni",
    "Juli",
    "Agustus",
    "September",
    "Oktober",
    "November",
    "Desember",
  ];
  return months[monthNumber - 1];
}

// Function to get storage key for current month
function getMonthStorageKey() {
  return `transactions_${monthSelect.value}`;
}

// Function to update table with new transaction
function updateTable(transaction, isInitialLoad = false) {
  const table = document
    .getElementById("finance-table")
    .getElementsByTagName("tbody")[0];
  const newRow = table.insertRow();

  // Calculate new balance based on transaction type
  if (!isInitialLoad) {
    if (transaction.type === "debit") {
      currentBalance += parseFloat(transaction.amount);
    } else {
      currentBalance -= parseFloat(transaction.amount);
    }
  }

  // Update row cells
  newRow.innerHTML = `
    <td>${transaction.date}</td>
    <td>${transaction.name}</td>
    <td>${transaction.type === "kredit" ? "Pengeluaran" : "Pemasukan"}</td>
    <td>${formatCurrency(transaction.amount)}</td>
    <td>${transaction.note}</td>
    <td>${formatCurrency(transaction.balance)}</td>
    <td><button class="delete-btn">Hapus</button></td>
  `;

  // Add event listener to delete button
  const deleteBtn = newRow.querySelector(".delete-btn");
  deleteBtn.addEventListener("click", () => {
    deleteTransaction(newRow, transaction);
  });

  // Update balance display
  updateBalanceDisplay();
}

// Function to delete a transaction
function deleteTransaction(row, transaction) {
  const confirmDelete = confirm(
    "Apakah Anda yakin ingin menghapus transaksi ini?"
  );
  if (!confirmDelete) return;

  // Get all transactions for current month
  const transactions = getTransactionsFromStorage();

  // Find and remove the transaction
  const updatedTransactions = transactions.filter(
    (t) =>
      !(
        t.date === transaction.date &&
        t.amount === transaction.amount &&
        t.name === transaction.name
      )
  );

  // Recalculate balances for all remaining transactions
  currentBalance = 0;
  updatedTransactions.forEach((t) => {
    if (t.type === "debit") {
      currentBalance += parseFloat(t.amount);
    } else {
      currentBalance -= parseFloat(t.amount);
    }
    t.balance = currentBalance;
  });

  // Save updated transactions
  localStorage.setItem(
    getMonthStorageKey(),
    JSON.stringify(updatedTransactions)
  );

  // Reload the table
  loadTransactions();
}

// Function to update balance display
function updateBalanceDisplay() {
  const monthName = getMonthName(parseInt(monthSelect.value));
  balanceDisplay.textContent = `Saldo ${monthName}: ${formatCurrency(
    currentBalance
  )}`;
}

// Function to get transactions from localStorage for current month
function getTransactionsFromStorage() {
  const transactions = localStorage.getItem(getMonthStorageKey());
  return transactions ? JSON.parse(transactions) : [];
}

// Function to validate transaction date matches selected month
function validateTransactionDate(date) {
  const transactionDate = new Date(date);
  const transactionMonth = transactionDate.getMonth() + 1;
  const selectedMonth = parseInt(monthSelect.value);
  return transactionMonth === selectedMonth;
}

// Handle form submission
form.addEventListener("submit", function (event) {
  event.preventDefault();

  const dateInput = document.getElementById("date");
  const amountInput = document.getElementById("amount");
  const amount = parseFloat(amountInput.value);

  // Validate amount
  if (isNaN(amount) || amount <= 0 || amount > 10000000) {
    alert("Masukkan jumlah yang valid (lebih dari 0 dan kurang dari 10 juta)");
    return;
  }

  // Validate date matches selected month
  if (!validateTransactionDate(dateInput.value)) {
    alert(
      `Tanggal harus sesuai dengan bulan ${getMonthName(
        parseInt(monthSelect.value)
      )}`
    );
    return;
  }

  // Calculate new balance
  const newBalance =
    currentBalance +
    (document.getElementById("type").value === "debit" ? amount : -amount);

  const transaction = {
    date: dateInput.value,
    name: document.getElementById("name").value,
    type: document.getElementById("type").value,
    amount: amount,
    note: document.getElementById("note").value,
    balance: newBalance,
  };

  // Get existing transactions and add new one
  const transactions = getTransactionsFromStorage();
  transactions.push(transaction);

  // Sort transactions by date
  transactions.sort((a, b) => new Date(a.date) - new Date(b.date));

  // Save to localStorage
  localStorage.setItem(getMonthStorageKey(), JSON.stringify(transactions));

  // Reload the table
  loadTransactions();

  // Reset form
  form.reset();

  // Set date input to current date
  const today = new Date();
  dateInput.value = today.toISOString().split("T")[0];
});

// Function to load transactions for selected month
function loadTransactions() {
  const transactions = getTransactionsFromStorage();
  tableBody.innerHTML = ""; // Clear existing rows
  currentBalance = 0; // Reset balance

  // Sort transactions by date
  transactions.sort((a, b) => new Date(a.date) - new Date(b.date));

  // Load each transaction
  transactions.forEach((transaction) => {
    if (transaction.type === "debit") {
      currentBalance += parseFloat(transaction.amount);
    } else {
      currentBalance -= parseFloat(transaction.amount);
    }
    transaction.balance = currentBalance;
    updateTable(transaction, true);
  });

  // Save transactions with updated balances
  localStorage.setItem(getMonthStorageKey(), JSON.stringify(transactions));
  updateBalanceDisplay();
}

// Handle month selection change
function loadData() {
  loadTransactions();

  // Set date input to first day of selected month
  const dateInput = document.getElementById("date");
  const selectedMonth = parseInt(monthSelect.value);
  const currentYear = new Date().getFullYear();
  const firstDayOfMonth = new Date(currentYear, selectedMonth - 1, 1);
  dateInput.value = firstDayOfMonth.toISOString().split("T")[0];
}

// Handle PDF download with improved styling
downloadPdfBtn.addEventListener("click", function () {
  const { jsPDF } = window.jspdf;
  const doc = new jsPDF();

  const monthName = getMonthName(parseInt(monthSelect.value));

  // Set up PDF styles
  doc.setFont("helvetica", "normal");
  doc.setTextColor(0, 0, 0); // Black text color

  // Title
  doc.setFontSize(16); // Reduced font size for title
  doc.text(`Laporan Keuangan - ${monthName}`, 14, 20);

  // Add header section
  doc.setFontSize(10); // Smaller font size for table headers
  const headerY = 30;
  const headers = ["Tanggal", "Nama", "Tipe", "Jumlah", "Catatan", "Saldo"];
  const headerPositions = [10, 30, 55, 90, 120, 150];

  // Header background color
  doc.setFillColor(50, 50, 50); // Dark grey background
  doc.rect(10, headerY - 6, 190, 8, "F");

  headers.forEach((header, index) => {
    doc.setTextColor(255, 255, 255); // White text color for header
    doc.text(header, headerPositions[index], headerY);
  });

  // Add transaction data
  let startY = headerY + 10;
  const transactions = getTransactionsFromStorage();

  transactions.forEach((transaction) => {
    const row = [
      transaction.date,
      transaction.name,
      transaction.type === "kredit" ? "Pengeluaran" : "Pemasukan",
      formatCurrency(transaction.amount),
      transaction.note,
      formatCurrency(transaction.balance),
    ];

    // Draw each row in the table with adjusted line height
    row.forEach((cell, index) => {
      doc.setTextColor(0, 0, 0); // Reset to black text
      doc.text(String(cell), headerPositions[index], startY);
    });

    startY += 8; // Reduced line spacing
    if (startY > 270) {
      doc.addPage();
      startY = 20;
    }
  });

  // Draw a footer line
  doc.setDrawColor(50, 50, 50); // Grey line
  doc.line(10, startY, 200, startY);

  // Footer with date and page number
  doc.setFontSize(9); // Slightly smaller font size for footer
  doc.text(
    `Tanggal Cetak: ${new Date().toLocaleDateString("id-ID")}`,
    10,
    startY + 5
  );
  doc.text(`Halaman ${doc.internal.getNumberOfPages()}`, 180, startY + 5);

  // Save PDF
  doc.save(`Laporan_Keuangan_${monthName}.pdf`);
});

// Initial load of current month's transactions
window.addEventListener("load", loadTransactions);
