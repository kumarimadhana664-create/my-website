const express = require('express');
const fs = require('fs');
const path = require('path');

const app = express();
const port = process.env.PORT || 3000;
const dataDirectory = path.join(__dirname, 'data');
const dataFile = path.join(dataDirectory, 'submissions.json');

app.use(express.json());
app.use(express.urlencoded({ extended: false }));
app.use(express.static(__dirname));

function readSubmissions() {
  if (!fs.existsSync(dataFile)) return { contacts: [], subscribers: [] };
  return JSON.parse(fs.readFileSync(dataFile, 'utf8'));
}

function saveSubmissions(submissions) {
  fs.mkdirSync(dataDirectory, { recursive: true });
  fs.writeFileSync(dataFile, JSON.stringify(submissions, null, 2));
}

function requiredString(value) {
  return typeof value === 'string' && value.trim().length > 0;
}

function validEmail(value) {
  return typeof value === 'string' && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value.trim());
}

app.get('/api/health', (request, response) => response.json({ status: 'ok' }));

app.post('/api/contact', (request, response) => {
  const { name, email, subject, message } = request.body;
  if (![name, subject, message].every(requiredString) || !validEmail(email)) {
    return response.status(400).json({ error: 'Please provide a name, valid email, subject, and message.' });
  }

  const submissions = readSubmissions();
  submissions.contacts.push({
    name: name.trim(), email: email.trim().toLowerCase(), subject: subject.trim(),
    message: message.trim(), createdAt: new Date().toISOString()
  });
  saveSubmissions(submissions);
  return response.status(201).json({ message: 'Your message has been sent.' });
});

app.post('/api/subscribe', (request, response) => {
  const { email } = request.body;
  if (!validEmail(email)) return response.status(400).json({ error: 'Please provide a valid email address.' });

  const submissions = readSubmissions();
  const normalizedEmail = email.trim().toLowerCase();
  if (!submissions.subscribers.some((subscriber) => subscriber.email === normalizedEmail)) {
    submissions.subscribers.push({ email: normalizedEmail, createdAt: new Date().toISOString() });
    saveSubmissions(submissions);
  }
  return response.status(201).json({ message: 'You are now subscribed to the Atelier Circle.' });
});

app.use('/api', (request, response) => response.status(404).json({ error: 'API route not found.' }));

app.listen(port, () => console.log(`Fashion.co is running at http://localhost:${port}`));