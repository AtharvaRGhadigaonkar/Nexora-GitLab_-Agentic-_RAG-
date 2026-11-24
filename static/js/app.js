
const chat = document.getElementById('chat');
const form = document.getElementById('chatForm');
const question = document.getElementById('question');
const trace = document.getElementById('trace');
const sourceUsed = document.getElementById('sourceUsed');

const askBtn = form.querySelector('button');
const modal = document.getElementById('uploadModal');
const uploadBtn = document.getElementById('uploadBtn');
const uploadStatus = document.getElementById('uploadStatus');


// --------------------
// Utility Functions
// --------------------

function escapeHtml(s = '') {
    return String(s).replace(/[&<>'"]/g, c => ({
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        "'": '&#39;',
        '"': '&quot;'
    }[c]));
}

function formatText(s = '') {
    return escapeHtml(s).replace(/\n/g, '<br>');
}


// --------------------
// Chat Messages
// --------------------

function addMessage(role, text, source = '', citations = []) {

    const wrap = document.createElement('div');
    wrap.className = `message ${role}`;

    const avatar = role === 'assistant' ? 'N' : 'U';

    const citeHtml = citations.length
        ? `
            <div class="citations">
                <strong>Retrieved References</strong>
                <br>
                ${citations.map(c =>
                    c.url
                        ? `<a href="${escapeHtml(c.url)}" target="_blank" rel="noopener noreferrer">${escapeHtml(c.title)}</a>`
                        : escapeHtml(c.title)
                ).join('<br>')}
            </div>
        `
        : '';

    wrap.innerHTML = `
        <div class="avatar">${avatar}</div>

        <div class="bubble">
            ${formatText(text)}

            ${source
                ? `<div class="answer-source">◈ ${escapeHtml(source)}</div>`
                : ''
            }

            ${citeHtml}
        </div>
    `;

    chat.appendChild(wrap);
    chat.scrollTop = chat.scrollHeight;
}


// --------------------
// Agent Activity Trace
// --------------------

function renderTrace(items = []) {

    trace.innerHTML = items.length
        ? items.map((item, index) => `
            <div class="trace-item">
                <span style="color:#fc6d26;font-weight:700;">
                    ${String(index + 1).padStart(2, '0')}
                </span>
                &nbsp; ${escapeHtml(item)}
            </div>
        `).join('')
        : '<div class="empty">No agent activity recorded.</div>';
}


// --------------------
// API Response Handling
// --------------------

async function readResponse(res) {

    const contentType = res.headers.get('content-type') || '';

    if (!contentType.includes('application/json')) {
        throw new Error(`Unexpected server response (${res.status}).`);
    }

    const data = await res.json();

    if (!res.ok) {
        throw new Error(data.detail || 'Request failed.');
    }

    return data;
}


// --------------------
// Ask Nexora
// --------------------

async function askAgent(q) {

    if (!q.trim()) return;

    addMessage('user', q);

    question.value = '';

    renderTrace([
        'Classifying incoming query...',
        'Initializing retrieval workflow...'
    ]);

    sourceUsed.textContent = 'Processing';

    askBtn.disabled = true;
    askBtn.textContent = 'Thinking...';

    try {

        const res = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                question: q
            })
        });

        const data = await readResponse(res);

        addMessage(
            'assistant',
            data.answer,
            data.source_used,
            data.citations || []
        );

        renderTrace(data.trace || []);

        sourceUsed.textContent = data.source_used || 'Unknown';

    } catch (error) {

        addMessage(
            'assistant',
            `I couldn't process your request.\n\n${error.message}`
        );

        renderTrace([
            'Query execution failed.',
            'Check the backend server and try again.'
        ]);

        sourceUsed.textContent = 'Error';

    } finally {

        askBtn.disabled = false;
        askBtn.textContent = 'Ask Nexora →';
        question.focus();

    }
}


// --------------------
// Chat Events
// --------------------

form.addEventListener('submit', e => {

    e.preventDefault();

    const q = question.value.trim();

    if (q) {
        askAgent(q);
    }

});

// Enter to send, Shift + Enter for newline
question.addEventListener('keydown', e => {

    if (e.key === 'Enter' && !e.shiftKey) {

        e.preventDefault();
        form.requestSubmit();

    }

});

// Example prompts
document.querySelectorAll('.example').forEach(button => {

    button.addEventListener('click', () => {

        if (!askBtn.disabled) {
            askAgent(button.textContent.trim());
        }

    });

});


// --------------------
// Document Upload Modal
// --------------------

document.getElementById('openUpload').onclick = () => {
    modal.classList.remove('hidden');
};

document.getElementById('closeUpload').onclick = () => {
    modal.classList.add('hidden');
};

// Close modal when clicking outside
modal.addEventListener('click', e => {

    if (e.target === modal) {
        modal.classList.add('hidden');
    }

});


// --------------------
// Import Knowledge
// --------------------

uploadBtn.onclick = async () => {

    const file = document.getElementById('fileInput').files[0];
    const key = document.getElementById('adminKey').value;

    if (!file) {
        uploadStatus.textContent = 'Please select a document first.';
        return;
    }

    uploadBtn.disabled = true;
    uploadBtn.textContent = 'Indexing...';

    uploadStatus.textContent = 'Processing document and generating embeddings...';

    const fd = new FormData();
    fd.append('file', file);

    try {

        const response = await fetch('/api/ingest', {
            method: 'POST',
            headers: {
                'X-Admin-Key': key
            },
            body: fd
        });

        const data = await readResponse(response);

        uploadStatus.textContent =
            `✓ Successfully indexed ${data.file}: ${data.chunks} chunks added to the knowledge base.`;

        uploadStatus.style.color = '#2eb67d';

    } catch (error) {

        uploadStatus.textContent = `Import failed: ${error.message}`;
        uploadStatus.style.color = '#fc6d26';

    } finally {

        uploadBtn.disabled = false;
        uploadBtn.textContent = 'Import & Index Document';

    }

};
