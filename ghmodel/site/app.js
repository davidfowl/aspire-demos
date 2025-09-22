const quoteEl = document.getElementById('quoteText');
const generateBtn = document.getElementById('generateBtn');
const copyBtn = document.getElementById('copyBtn');
const statusEl = document.getElementById('status');

let currentQuote = '';

function setLoading(isLoading) {
  quoteEl.parentElement.setAttribute('aria-busy', isLoading ? 'true' : 'false');
  generateBtn.disabled = isLoading;
  statusEl.textContent = isLoading ? 'Generating…' : '';
  if (isLoading) {
    quoteEl.classList.add('loading');
  } else {
    quoteEl.classList.remove('loading');
  }
}

async function fetchQuote() {
  setLoading(true);
  statusEl.classList.remove('error');
  try {
    const res = await fetch('/quote', { headers: { 'Accept': 'application/json' } });
    if (!res.ok) {
      const body = await res.json().catch(() => ({}));
      throw new Error(body.error || `Request failed (${res.status})`);
    }
    const data = await res.json();
    currentQuote = data.quote || '';
    if (!currentQuote) throw new Error('Empty quote received');
    quoteEl.textContent = currentQuote;
    quoteEl.classList.remove('placeholder');
    copyBtn.disabled = false;
    statusEl.textContent = 'Done';
  } catch (err) {
    console.error(err);
    statusEl.textContent = err.message;
    statusEl.classList.add('error');
    copyBtn.disabled = true;
  } finally {
    setLoading(false);
  }
}

async function copyQuote() {
  if (!currentQuote) return;
  try {
    await navigator.clipboard.writeText(currentQuote);
    statusEl.textContent = 'Copied to clipboard';
    statusEl.classList.remove('error');
  } catch {
    statusEl.textContent = 'Copy failed';
    statusEl.classList.add('error');
  }
}

function handleKey(e) {
  if ((e.key === 'Enter' && (e.metaKey || e.ctrlKey)) || (e.key === 'Enter' && document.activeElement !== generateBtn)) {
    e.preventDefault();
    generateBtn.click();
  }
}

generateBtn.addEventListener('click', fetchQuote);
copyBtn.addEventListener('click', copyQuote);
window.addEventListener('keydown', handleKey);

// Optional: auto-generate first quote after slight delay
setTimeout(() => {
  if (quoteEl.classList.contains('placeholder')) {
    fetchQuote();
  }
}, 400);
