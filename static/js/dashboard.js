document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('summaryForm');
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const summaryOutput = document.getElementById('summaryOutput');
    const progressBar = document.getElementById('progressBar');
    const progressWrapper = document.querySelector('.progress-wrapper');
    const toastContainer = document.getElementById('toastContainer');
    const copyButton = document.getElementById('copySummaryBtn');
    const downloadPdfBtn = document.getElementById('downloadPdfBtn');
    const downloadDocxBtn = document.getElementById('downloadDocxBtn');
    const keywordsValue = document.getElementById('keywordsValue');
    const readingTimeValue = document.getElementById('readingTimeValue');
    const wordCountValue = document.getElementById('wordCountValue');
    const charCountValue = document.getElementById('charCountValue');
    const historyTableBody = document.getElementById('historyTableBody');
    const historySearch = document.getElementById('historySearch');
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.querySelector('.dashboard-sidebar');
    let currentSummaryId = null;

    const showToast = (message, type = 'success') => {
        const toast = document.createElement('div');
        toast.className = 'toast-item';
        toast.innerHTML = `<strong>${type === 'error' ? 'Error' : 'Success'}</strong><div>${message}</div>`;
        toastContainer.appendChild(toast);
        setTimeout(() => toast.remove(), 3300);
    };

    const renderHistory = (items) => {
        if (!historyTableBody) return;
        historyTableBody.innerHTML = '';
        if (!items.length) {
            historyTableBody.innerHTML = '<tr><td colspan="5" class="text-center py-4">No summaries yet. Start by uploading your first document.</td></tr>';
            return;
        }

        items.forEach((item) => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${item.filename}</td>
                <td>${item.summary.slice(0, 120)}${item.summary.length > 120 ? '...' : ''}</td>
                <td>${item.keywords}</td>
                <td>${item.created_at}</td>
                <td>
                    <a class="btn btn-sm btn-outline-light" href="/download/${item.id}/pdf"><i class="bi bi-download me-1"></i>PDF</a>
                    <button class="btn btn-sm btn-outline-light delete-btn" data-id="${item.id}" type="button"><i class="bi bi-trash me-1"></i>Delete</button>
                </td>`;
            historyTableBody.appendChild(row);
        });
    };

    const animateProgress = (value) => {
        progressWrapper.style.display = 'block';
        progressBar.style.width = `${value}%`;
    };

    const resetProgress = () => {
        progressBar.style.width = '0%';
        progressWrapper.style.display = 'none';
    };

    if (form) {
        form.addEventListener('submit', async (event) => {
            event.preventDefault();
            const formData = new FormData(form);
            animateProgress(30);
            try {
                const response = await fetch('/summarize', {
                    method: 'POST',
                    body: formData,
                });
                const data = await response.json();
                animateProgress(100);
                if (!data.success) {
                    showToast(data.message, 'error');
                    summaryOutput.innerHTML = `<div class="empty-state"><i class="bi bi-exclamation-triangle"></i><h4>Unable to generate summary</h4><p>${data.message}</p></div>`;
                    resetProgress();
                    return;
                }
                summaryOutput.innerHTML = `<div>${data.summary}</div>`;
                keywordsValue.textContent = data.keywords.join(', ') || '—';
                readingTimeValue.textContent = data.reading_time;
                wordCountValue.textContent = data.word_count;
                charCountValue.textContent = data.char_count;
                downloadPdfBtn.href = `/download/${data.summary_id}/pdf`;
                downloadDocxBtn.href = `/download/${data.summary_id}/docx`;
                currentSummaryId = data.summary_id;
                renderHistory(data.history);
                showToast(data.message);
                setTimeout(resetProgress, 450);
            } catch (error) {
                showToast('A network error occurred while generating the summary.', 'error');
                resetProgress();
            }
        });
    }

    ['dragenter', 'dragover'].forEach((eventName) => {
        dropZone.addEventListener(eventName, (event) => {
            event.preventDefault();
            dropZone.classList.add('drag-over');
        });
    });

    ['dragleave', 'drop'].forEach((eventName) => {
        dropZone.addEventListener(eventName, (event) => {
            event.preventDefault();
            dropZone.classList.remove('drag-over');
        });
    });

    dropZone.addEventListener('drop', (event) => {
        const files = event.dataTransfer.files;
        if (files.length) {
            fileInput.files = files;
        }
    });

    dropZone.addEventListener('click', () => fileInput.click());

    if (copyButton) {
        copyButton.addEventListener('click', async () => {
            const text = summaryOutput.innerText;
            if (!text || text.includes('Your summary will appear here')) return;
            await navigator.clipboard.writeText(text);
            showToast('Summary copied to clipboard.');
        });
    }

    if (historySearch) {
        historySearch.addEventListener('input', async (event) => {
            const query = event.target.value.toLowerCase();
            const response = await fetch('/history_data');
            const items = await response.json();
            const filtered = items.filter((item) => item.filename.toLowerCase().includes(query) || item.summary.toLowerCase().includes(query));
            renderHistory(filtered);
        });
    }

    document.addEventListener('click', async (event) => {
        const button = event.target.closest('.delete-btn');
        if (!button) return;
        const id = button.getAttribute('data-id');
        const response = await fetch(`/delete_history/${id}`, { method: 'POST' });
        const data = await response.json();
        if (data.success) {
            showToast(data.message);
            const responseHistory = await fetch('/history_data');
            const historyItems = await responseHistory.json();
            renderHistory(historyItems);
        }
    });

    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', () => {
            sidebar.classList.toggle('d-none');
        });
    }
});
