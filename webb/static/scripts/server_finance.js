const express = require("express");
const fs = require("fs");
const bodyParser = require("body-parser");
const path = require("path");

const app = express();
const PORT = 3000;
const DATA_PATH = path.join(__dirname, "data", "transactions.csv");

// Middleware
app.use(bodyParser.json());
app.use(express.static("public"));

// Endpoint untuk mendapatkan data transaksi
app.get("/transactions", (req, res) => {
  if (!fs.existsSync(DATA_PATH)) {
    return res.json([]);
  }
  const data = fs.readFileSync(DATA_PATH, "utf8");
  const rows = data.split("\n").slice(1); // Skip header
  const transactions = rows
    .filter((row) => row.trim() !== "")
    .map((row) => {
      const [date, name, type, amount, note, saldo] = row.split(",");
      return { date, name, type, amount: parseFloat(amount), note, saldo };
    });
  res.json(transactions);
});

// Endpoint untuk menambahkan transaksi baru
app.post("/transactions", (req, res) => {
  const { date, name, type, amount, note, saldo } = req.body;

  // Tambahkan ke CSV file
  const newTransaction = `${date},${name},${type},${amount},${note},${saldo}\n`;
  const header = "date,name,type,amount,note,saldo\n";

  if (!fs.existsSync(DATA_PATH)) {
    fs.writeFileSync(DATA_PATH, header);
  }

  fs.appendFileSync(DATA_PATH, newTransaction, "utf8");
  res.json({ message: "Transaction saved!" });
});

app.listen(PORT, () => {
  console.log(`Server running at http://localhost:${PORT}`);
});
