const express = require('express');
const multer = require('multer');
const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const fs = require('fs');

const router = express.Router();

// Open or create sponsor.db SQLite database
const db = new sqlite3.Database(path.join(__dirname, 'sponsor.db'), (err) => {
  if (err) console.error("DB Open Error:", err.message);
  else console.log("Connected to sponsor SQLite DB.");
});

// Create table if not exists
db.run(`CREATE TABLE IF NOT EXISTS sponsor_profiles (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  company_name TEXT NOT NULL,
  gst_number TEXT,
  annual_turnover REAL,
  tax_registration_path TEXT
);`);

// Multer config for PDF uploads
const uploadDir = path.join(__dirname, 'uploads');
if (!fs.existsSync(uploadDir)) {
  fs.mkdirSync(uploadDir);
}

const storage = multer.diskStorage({
  destination: function (req, file, cb) { cb(null, uploadDir); },
  filename: function (req, file, cb) {
    cb(null, Date.now() + path.extname(file.originalname));
  }
});

const fileFilter = (req, file, cb) => {
  if (file.mimetype === 'application/pdf') cb(null, true);
  else cb(new Error('Only PDF files allowed'), false);
};

const upload = multer({ storage, fileFilter });

// API to get sponsor profile (returns first profile for demo)
router.get('/profile', (req, res) => {
  db.get("SELECT * FROM sponsor_profiles LIMIT 1", (err, row) => {
    if (err) {
      console.error(err);
      res.status(500).json({ error: "DB error" });
    } else {
      res.json({ profile: row || null });
    }
  });
});

// API to save sponsor profile
router.post('/profile', upload.single('taxRegistration'), (req, res) => {
  const { name, companyName, gstNumber, annualTurnover } = req.body;
  const file = req.file;

  if (!name || !companyName) {
    res.status(400).json({ message: "Name and company name required" });
    return;
  }

  const taxFilePath = file ? file.path : null;

  // For demo: delete existing profiles so only one is saved
  db.run("DELETE FROM sponsor_profiles", (err) => {
    if (err) console.error("Delete error:", err);

    const sql = `INSERT INTO sponsor_profiles (name, company_name, gst_number, annual_turnover, tax_registration_path) VALUES (?,?,?,?,?)`;
    db.run(sql, [name, companyName, gstNumber, annualTurnover, taxFilePath], function(err) {
      if (err) {
        console.error(err);
        res.status(500).json({ message: "DB insert error" });
      } else {
        res.json({ success: true, profileId: this.lastID });
      }
    });
  });
});

module.exports = router;
