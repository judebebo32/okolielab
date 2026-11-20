/**
 * SETD Student Hiring – application receiver (Google Apps Script web app)
 *
 * Receives applications from https://okolielab.netlify.app/student-hiring.html,
 * saves the three PDFs into a per-applicant folder in Google Drive and adds a
 * row with links to the "Applications" sheet.
 *
 * Setup (one time): open the response spreadsheet → Extensions → Apps Script,
 * paste this file, Save, then Deploy → New deployment → Web app,
 * Execute as: Me, Who has access: Anyone → Deploy → Authorize.
 * Copy the Web app URL (ends in /exec) into HIRING_ENDPOINT in src/build.py.
 */

const SHEET_ID  = '1AVRQevhRP3QX6HC7Fyap8ipx2NXmqcbMH_dIwI_3k_0'; // SETD Student Hiring – Applications (responses)
const FOLDER_ID = '1BCQI0_mpTrnyW1Uv4OVz9-Q2ySFGz8y1';             // Applicant documents
const SHEET_NAME = 'Applications';

// Optional: put an address here to get an email each time someone applies (leave '' for none).
const NOTIFY_EMAIL = '';

const MAX_FILE_BYTES = 5 * 1024 * 1024;  // 5 MB per document
const DOCS = [
  ['coverLetter', 'Cover letter'],
  ['cv', 'CV'],
  ['proposal', 'Research proposal'],
];

function doPost(e) {
  const lock = LockService.getScriptLock();
  try {
    const d = JSON.parse(e.postData.contents);

    // Spam trap: real applicants never fill the hidden "website" field.
    if (d.website) return json_({ ok: true });

    const name = clean_(d.name, 120);
    const email = clean_(d.email, 200);
    if (!name || !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) throw new Error('Please give your name and a valid email address.');
    if (!d.aiConfirm) throw new Error('Please confirm the AI-use statement.');

    const stamp = Utilities.formatDate(new Date(), 'America/New_York', 'yyyy-MM-dd HH:mm');
    const parent = DriveApp.getFolderById(FOLDER_ID);
    const folder = parent.createFolder(stamp + ' – ' + name);

    const links = DOCS.map(function (doc) {
      const f = d[doc[0]];
      if (!f || !f.data) throw new Error('Missing file: ' + doc[1] + '.');
      const bytes = Utilities.base64Decode(f.data);
      if (bytes.length > MAX_FILE_BYTES) throw new Error(doc[1] + ' is larger than 5 MB.');
      if (String.fromCharCode.apply(null, bytes.slice(0, 4)) !== '%PDF') throw new Error(doc[1] + ' must be a PDF file.');
      const blob = Utilities.newBlob(bytes, 'application/pdf', doc[1] + ' – ' + name + '.pdf');
      return folder.createFile(blob).getUrl();
    });

    lock.waitLock(20000);
    const sheet = SpreadsheetApp.openById(SHEET_ID).getSheetByName(SHEET_NAME) ||
                  SpreadsheetApp.openById(SHEET_ID).getSheets()[0];
    sheet.appendRow([
      stamp, name, email,
      clean_(d.degree, 40),
      clean_(d.projects, 300),
      clean_(d.institution, 200),
      clean_(d.aiUsed, 10),
      clean_(d.aiStatement, 3000),
      link_(links[0], 'Cover letter'),
      link_(links[1], 'CV'),
      link_(links[2], 'Proposal'),
      link_(folder.getUrl(), 'Folder'),
    ]);

    if (NOTIFY_EMAIL) {
      MailApp.sendEmail(NOTIFY_EMAIL, 'New SETD application: ' + name,
        name + ' (' + email + ') applied for ' + clean_(d.degree, 40) + ' – ' + clean_(d.projects, 300) +
        '\n\nDocuments: ' + folder.getUrl() +
        '\nSpreadsheet: https://docs.google.com/spreadsheets/d/' + SHEET_ID);
    }
    return json_({ ok: true });
  } catch (err) {
    return json_({ ok: false, error: String(err.message || err) });
  } finally {
    try { lock.releaseLock(); } catch (x) {}
  }
}

function doGet() {
  return json_({ ok: true, service: 'SETD student hiring form' });
}

function clean_(v, max) {
  // Strip leading = + - @ so text can never run as a spreadsheet formula.
  return String(v == null ? '' : v).trim().replace(/^[=+\-@]+/, '').slice(0, max);
}

function link_(url, label) {
  return '=HYPERLINK("' + url + '","' + label + '")';
}

function json_(o) {
  return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON);
}
