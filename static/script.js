// ---------- Tab navigation ----------
const tabButtons = document.querySelectorAll('.tab-btn');
const tabPanels = document.querySelectorAll('.tab-panel');

tabButtons.forEach(btn => {
  btn.addEventListener('click', () => {
    tabButtons.forEach(b => b.classList.remove('active'));
    tabPanels.forEach(p => p.classList.remove('active'));
    btn.classList.add('active');
    document.getElementById(btn.dataset.tab).classList.add('active');

    if (btn.dataset.tab === 'search') loadDonors();
    if (btn.dataset.tab === 'dashboard') { loadStats(); loadRequests(); }
  });
});

// ---------- Helpers ----------
function showMessage(elId, text, type) {
  const el = document.getElementById(elId);
  el.textContent = text;
  el.className = 'form-message ' + type;
  setTimeout(() => { el.className = 'form-message'; }, 4000);
}

function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str ?? '';
  return div.innerHTML;
}

function bgClass(group) {
  return 'bg-' + group.replace('+', '\\+').replace('-', '\\-');
}

// ---------- Register form ----------
document.getElementById('register-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const form = e.target;
  const data = Object.fromEntries(new FormData(form).entries());

  try {
    const res = await fetch('/api/donors', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    const result = await res.json();
    if (res.ok) {
      showMessage('register-message', result.message || 'Donor registered!', 'success');
      form.reset();
    } else {
      showMessage('register-message', (result.errors || ['Something went wrong.']).join(' '), 'error');
    }
  } catch (err) {
    showMessage('register-message', 'Network error. Please try again.', 'error');
  }
});

// ---------- Search / filter donors ----------
async function loadDonors() {
  const bloodGroup = document.getElementById('filter-blood-group').value;
  const location = document.getElementById('filter-location').value;

  const params = new URLSearchParams();
  if (bloodGroup) params.set('blood_group', bloodGroup);
  if (location) params.set('location', location);

  const res = await fetch('/api/donors?' + params.toString());
  const donors = await res.json();

  const grid = document.getElementById('donor-results');
  const noResults = document.getElementById('no-results');
  grid.innerHTML = '';

  if (donors.length === 0) {
    noResults.style.display = 'block';
    return;
  }
  noResults.style.display = 'none';

  donors.forEach(d => {
    const card = document.createElement('div');
    card.className = 'donor-card';
    const availClass = d.availability === 'Available' ? 'badge-avail' : 'badge-unavail';
    card.innerHTML = `
      <div class="donor-card-top">
        <p class="donor-name">${escapeHtml(d.name)}</p>
        <span class="badge ${bgClass(d.blood_group)}">${escapeHtml(d.blood_group)}</span>
      </div>
      <p class="donor-meta">📍 ${escapeHtml(d.location)}</p>
      <p class="donor-meta">📞 ${escapeHtml(d.phone)}</p>
      <span class="badge ${availClass}">${escapeHtml(d.availability)}</span>
    `;
    grid.appendChild(card);
  });
}

document.getElementById('filter-blood-group').addEventListener('change', loadDonors);
document.getElementById('filter-location').addEventListener('input', debounce(loadDonors, 250));

function debounce(fn, delay) {
  let timer;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), delay);
  };
}

// ---------- Request form ----------
document.getElementById('request-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const form = e.target;
  const data = Object.fromEntries(new FormData(form).entries());

  try {
    const res = await fetch('/api/requests', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    const result = await res.json();
    if (res.ok) {
      showMessage('request-message', result.message || 'Request submitted!', 'success');
      form.reset();
    } else {
      showMessage('request-message', (result.errors || ['Something went wrong.']).join(' '), 'error');
    }
  } catch (err) {
    showMessage('request-message', 'Network error. Please try again.', 'error');
  }
});

// ---------- Dashboard ----------
async function loadStats() {
  const res = await fetch('/api/stats');
  const stats = await res.json();
  document.getElementById('stat-total-donors').textContent = stats.total_donors;
  document.getElementById('stat-available-donors').textContent = stats.available_donors;
  document.getElementById('stat-pending-requests').textContent = stats.pending_requests;
}

async function loadRequests() {
  const res = await fetch('/api/requests');
  const requests = await res.json();
  const tbody = document.getElementById('requests-tbody');
  const noRequests = document.getElementById('no-requests');
  tbody.innerHTML = '';

  if (requests.length === 0) {
    noRequests.style.display = 'block';
    return;
  }
  noRequests.style.display = 'none';

  requests.forEach(r => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${escapeHtml(r.patient_name)}</td>
      <td><span class="badge ${bgClass(r.blood_group)}">${escapeHtml(r.blood_group)}</span></td>
      <td>${escapeHtml(r.hospital)}</td>
      <td>${escapeHtml(r.location)}</td>
      <td>${escapeHtml(r.contact_number)}</td>
      <td>${escapeHtml(r.created_at)}</td>
    `;
    tbody.appendChild(tr);
  });
}

// ---------- Initial load ----------
loadDonors();
loadStats();
loadRequests();
