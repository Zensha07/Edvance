const express = require('express');
const multer = require('multer');
const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = 3000;

// Create uploads directory if it doesn't exists
const uploadDir = path.join(__dirname, 'uploads');
if (!fs.existsSync(uploadDir)) {
  fs.mkdirSync(uploadDir);
}

// Multer setup for file uploads (PDF only)
const storage = multer.diskStorage({
  destination: (req, file, cb) => cb(null, uploadDir),
  filename: (req, file, cb) => cb(null, Date.now() + path.extname(file.originalname))
});
const fileFilter = (req, file, cb) => {
  if (file.mimetype === 'application/pdf') cb(null, true);
  else cb(new Error('Only PDF files are allowed'));
};
const upload = multer({ storage, fileFilter });

// Initialize SQLite DB
const db = new sqlite3.Database(path.join(__dirname, 'sponsor.db'), (err) => {
  if (err) return console.error(err.message);
  console.log('Connected to SQLite database.');
});

// Create table if it does not exist
db.run(`CREATE TABLE IF NOT EXISTS sponsor_profiles (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  company_name TEXT NOT NULL,
  gst_number TEXT,
  annual_turnover REAL,
  tax_registration_path TEXT
)`);

// Middleware to parse JSON & serve frontend files
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static(path.join(__dirname, '../frontend/Sponsor'))); // adjust if your frontend folder is different

// Get sponsor profile (return first record for demo)
app.get('/api/sponsor/profile', (req, res) => {
  db.get("SELECT * FROM sponsor_profiles LIMIT 1", (err, row) => {
    if (err) return res.status(500).json({ error: err.message });
    res.json({ profile: row || null });
  });
});

// Save or update sponsor profile
app.post('/api/sponsor/profile', upload.single('taxRegistration'), (req, res) => {
  const { name, companyName, gstNumber, annualTurnover } = req.body;
  const taxFile = req.file;

  if (!name || !companyName) {
    return res.status(400).json({ success: false, message: 'Name and Company Name are required.' });
  }

  const taxFilePath = taxFile ? taxFile.path : null;

  // Delete existing data (for demo, only one profile stored)
  db.run("DELETE FROM sponsor_profiles", (err) => {
    if (err) console.error(err);

    const sql = `INSERT INTO sponsor_profiles (name, company_name, gst_number, annual_turnover, tax_registration_path)
                 VALUES (?, ?, ?, ?, ?)`;
    db.run(sql, [name, companyName, gstNumber || '', annualTurnover || 0, taxFilePath], function(err) {
      if (err) {
        console.error(err.message);
        res.status(500).json({ success: false, message: 'Database insert failed' });
      } else {
        res.json({ success: true });
      }
    });
  });
});

app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});

