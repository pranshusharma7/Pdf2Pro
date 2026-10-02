/**
 * PDF2Pro Converter Engine
 * Shared conversion logic for all tool pages.
 * Handles: file upload → animated progress → success (Download + Preview modal)
 */
(function () {
    'use strict';

    // ── Tool metadata ─────────────────────────────────────────
    const TOOL_MAP = {
        'pdf-to-word': { title: 'PDF to <span class="text-gradient">Word</span>', desc: 'Convert PDF files to editable Word documents instantly.', icon: 'document-text-outline', ext: 'docx', accept: '.pdf', supportedText: 'Supported: PDF (Max 50MB)' },
        'pdf-to-excel': { title: 'PDF to <span class="text-gradient">Excel</span>', desc: 'Extract tables from PDFs into editable Excel spreadsheets.', icon: 'grid-outline', ext: 'xlsx', accept: '.pdf', supportedText: 'Supported: PDF (Max 50MB)' },
        'pdf-to-ppt': { title: 'PDF to <span class="text-gradient">PPT</span>', desc: 'Convert PDF slides into editable PowerPoint presentations.', icon: 'easel-outline', ext: 'pptx', accept: '.pdf', supportedText: 'Supported: PDF (Max 50MB)' },
        'pdf-to-jpg': { title: 'PDF to <span class="text-gradient">JPG</span>', desc: 'Extract images or save PDF pages as high-quality JPGs.', icon: 'images-outline', ext: 'jpg', accept: '.pdf', supportedText: 'Supported: PDF (Max 50MB)' },
        'pdf-to-png': { title: 'PDF to <span class="text-gradient">PNG</span>', desc: 'Convert PDF pages to crisp PNG images.', icon: 'image-outline', ext: 'png', accept: '.pdf', supportedText: 'Supported: PDF (Max 50MB)' },
        'word-to-pdf': { title: 'Word to <span class="text-gradient">PDF</span>', desc: 'Securely convert Word documents into high-quality PDFs.', icon: 'document-outline', ext: 'pdf', accept: '.doc,.docx', supportedText: 'Supported: DOC, DOCX (Max 50MB)' },
        'excel-to-pdf': { title: 'Excel to <span class="text-gradient">PDF</span>', desc: 'Convert Excel spreadsheets to professional PDF documents.', icon: 'grid-outline', ext: 'pdf', accept: '.xls,.xlsx', supportedText: 'Supported: XLS, XLSX (Max 50MB)' },
        'ppt-to-pdf': { title: 'PPT to <span class="text-gradient">PDF</span>', desc: 'Convert PowerPoint to PDF with full fidelity.', icon: 'easel-outline', ext: 'pdf', accept: '.ppt,.pptx', supportedText: 'Supported: PPT, PPTX (Max 50MB)' },
        'jpg-to-pdf': { title: 'JPG to <span class="text-gradient">PDF</span>', desc: 'Combine JPG/PNG images into a single PDF document.', icon: 'images-outline', ext: 'pdf', accept: '.jpg,.jpeg,.png,.bmp,.gif,.webp', supportedText: 'Supported: JPG, PNG, BMP, GIF (Max 50MB)' },
        'merge-pdf': { title: '<span class="text-gradient">Merge</span> PDF', desc: 'Combine multiple PDF files into one clean document.', icon: 'git-merge-outline', ext: 'pdf', accept: '.pdf', supportedText: 'Supported: PDF – select multiple files' },
        'split-pdf': { title: '<span class="text-gradient">Split</span> PDF', desc: 'Split one PDF into multiple separate documents.', icon: 'cut-outline', ext: 'pdf', accept: '.pdf', supportedText: 'Supported: PDF (Max 50MB)' },
        'compress-pdf': { title: '<span class="text-gradient">Compress</span> PDF', desc: 'Reduce your PDF file size while preserving quality.', icon: 'archive-outline', ext: 'pdf', accept: '.pdf', supportedText: 'Supported: PDF (Max 50MB)' },
        'protect-pdf': { title: '<span class="text-gradient">Protect</span> PDF', desc: 'Add password protection to your PDF files.', icon: 'lock-closed-outline', ext: 'pdf', accept: '.pdf', supportedText: 'Supported: PDF (Max 50MB)' },
        'unlock-pdf': { title: '<span class="text-gradient">Unlock</span> PDF', desc: 'Remove password and restrictions from your PDF.', icon: 'lock-open-outline', ext: 'pdf', accept: '.pdf', supportedText: 'Supported: PDF (Max 50MB)' },
        'edit-pdf': { title: '<span class="text-gradient">Edit</span> PDF', desc: 'Edit text and images in your PDF documents.', icon: 'create-outline', ext: 'pdf', accept: '.pdf', supportedText: 'Supported: PDF (Max 50MB)' },
        'sign-pdf': { title: '<span class="text-gradient">Sign</span> PDF', desc: 'Add your digital signature to PDF documents.', icon: 'pencil-outline', ext: 'pdf', accept: '.pdf', supportedText: 'Supported: PDF (Max 50MB)' },
    };

    // ── Inject preview modal HTML once ───────────────────────
    function injectModal() {
        if (document.getElementById('preview-modal')) return;
        const modal = document.createElement('div');
        modal.id = 'preview-modal';
        modal.style.cssText = 'display:none;position:fixed;inset:0;z-index:9999;background:rgba(0,0,0,.72);backdrop-filter:blur(8px);align-items:center;justify-content:center;padding:16px;';
        modal.innerHTML = `
            <div style="background:var(--bg-surface,#fff);border-radius:18px;width:min(880px,100%);max-height:90vh;display:flex;flex-direction:column;box-shadow:0 24px 80px rgba(0,0,0,.5);overflow:hidden;">
                <div id="pm-head" style="display:flex;align-items:center;justify-content:space-between;padding:14px 20px;border-bottom:1px solid var(--border-color,#e5e7eb);">
                    <div style="display:flex;align-items:center;gap:10px;">
                        <ion-icon name="document-text-outline" style="font-size:1.3rem;color:var(--primary-500,#6366f1);"></ion-icon>
                        <span id="pm-title" style="font-weight:700;font-size:.95rem;color:var(--text-main,#111);max-width:400px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">Preview</span>
                    </div>
                    <div style="display:flex;gap:8px;align-items:center;">
                        <a id="pm-dl" href="#" download style="display:inline-flex;align-items:center;gap:6px;padding:7px 16px;border-radius:8px;background:var(--primary-600,#4f46e5);color:#fff;font-size:.82rem;font-weight:600;text-decoration:none;">
                            <ion-icon name="download-outline"></ion-icon> Download
                        </a>
                        <button id="pm-close" style="width:36px;height:36px;border-radius:8px;border:1px solid var(--border-color,#e5e7eb);background:transparent;cursor:pointer;display:grid;place-items:center;color:var(--text-muted,#6b7280);">
                            <ion-icon name="close-outline" style="font-size:1.3rem;"></ion-icon>
                        </button>
                    </div>
                </div>
                <div id="pm-body" style="flex:1;overflow:auto;background:#f1f5f9;display:flex;align-items:center;justify-content:center;min-height:420px;"></div>
            </div>`;
        document.body.appendChild(modal);
        document.getElementById('pm-close').onclick = closePreview;
        modal.addEventListener('click', e => { if (e.target === modal) closePreview(); });
    }

    function openPreview(url, filename) {
        const modal = document.getElementById('preview-modal');
        const body = document.getElementById('pm-body');
        document.getElementById('pm-title').textContent = filename;
        const dl = document.getElementById('pm-dl');
        dl.href = url; dl.setAttribute('download', filename);
        body.innerHTML = '<div style="text-align:center;color:#6b7280;padding:40px;"><ion-icon name="reload-outline" style="font-size:2.5rem;display:block;margin:0 auto 12px;animation:spin 1s linear infinite;"></ion-icon><p>Loading…</p></div>';
        modal.style.display = 'flex';
        document.body.style.overflow = 'hidden';
        const ext = filename.split('.').pop().toLowerCase();
        if (['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg'].includes(ext)) {
            body.innerHTML = `<img src="${url}" style="max-width:100%;max-height:76vh;object-fit:contain;border-radius:6px;box-shadow:0 4px 24px rgba(0,0,0,.2);margin:16px;">`;
        } else if (ext === 'pdf') {
            body.innerHTML = `<iframe src="${url}" style="width:100%;height:76vh;border:none;display:block;"></iframe>`;
        } else {
            body.innerHTML = `<iframe src="https://docs.google.com/gview?url=${encodeURIComponent(url)}&embedded=true" style="width:100%;height:76vh;border:none;display:block;" allowfullscreen></iframe>`;
        }
    }

    function closePreview() {
        const modal = document.getElementById('preview-modal');
        if (modal) { modal.style.display = 'none'; document.getElementById('pm-body').innerHTML = ''; }
        document.body.style.overflow = '';
    }

    // ── Progress bar animation ────────────────────────────────
    function animateProgress(bar, text, to, ms = 1200) {
        const from = parseFloat(bar.style.width) || 0;
        const diff = to - from, ts = performance.now();
        const tick = now => {
            const t = Math.min((now - ts) / ms, 1);
            const ease = t < .5 ? 2 * t * t : -1 + (4 - 2 * t) * t;
            const cur = from + diff * ease;
            bar.style.width = cur + '%';
            bar.style.background = 'linear-gradient(90deg,#6366f1,#a855f7,#ec4899)';
            bar.style.boxShadow = '0 0 16px rgba(99,102,241,.55)';
            text.innerText = Math.round(cur) + '%';
            if (t < 1) requestAnimationFrame(tick);
        };
        requestAnimationFrame(tick);
    }

    function formatServerDetails(details) {
        if (!details) return '';
        if (typeof details !== 'string') return JSON.stringify(details);
        try {
            const parsed = JSON.parse(details);
            if (parsed.Message) return parsed.Message;
            return JSON.stringify(parsed);
        } catch (_) {
            return details;
        }
    }

    // ── Main init ─────────────────────────────────────────────
    function init() {
        injectModal();

        // Detect tool ID from filename
        const fname = location.pathname.split('/').pop().replace('.html', '');
        const toolId = (fname && fname !== 'index' && fname !== 'convert') ? fname : 'pdf-to-word';
        const info = TOOL_MAP[toolId] || TOOL_MAP['pdf-to-word'];

        // Update page titles / badge
        const titleEl = document.getElementById('dynamic-tool-title');
        const descEl = document.getElementById('dynamic-tool-desc');
        const badgeEl = document.getElementById('dynamic-tool-badge');
        const labelEl = document.getElementById('dynamic-conversion-label');

        if (titleEl) titleEl.innerHTML = info.title;
        if (descEl) descEl.innerText = info.desc;
        if (badgeEl) badgeEl.innerHTML = `<ion-icon name="${info.icon}"></ion-icon> ${info.title.replace(/<[^>]*>/g, '')}`;
        if (labelEl) labelEl.innerHTML = `Click <b>Convert Now</b> to get your <b>${info.title.replace(/<[^>]*>/g, '')}</b>`;
        document.title = info.title.replace(/<[^>]*>/g, '') + ' – PDF2Pro';

        // Set correct file accept filter + supported formats text
        const fileInput2 = document.getElementById('file-input');
        if (fileInput2 && info.accept) fileInput2.setAttribute('accept', info.accept);
        const supportedEl = document.querySelector('.upload-zone p');
        if (supportedEl && info.supportedText) supportedEl.textContent = info.supportedText;

        // DOM refs
        const uploadZone = document.getElementById('upload-zone');
        const fileInput = document.getElementById('file-input');
        const convState = document.getElementById('conversion-state');
        const fileListCont = document.getElementById('file-list-container');
        const optBar = document.querySelector('.conversion-options-bar');
        const progCont = document.getElementById('progress-container');
        const progBar = document.getElementById('progress-bar');
        const progText = document.getElementById('progress-percent');
        const statusText = document.querySelector('.status-text');
        const succCont = document.getElementById('success-container');
        const downloadBtn = document.getElementById('download-result-btn');
        const previewBtn = document.getElementById('preview-result-btn');
        const convAnotherBtn = document.getElementById('convert-another-btn');
        const startBtn = document.getElementById('start-conversion-btn');

        if (!uploadZone || !startBtn) return; // Not a converter page

        let currentFiles = [], resultUrl = '', resultName = '';

        // ── Drag & drop ──
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(ev =>
            uploadZone.addEventListener(ev, e => { e.preventDefault(); e.stopPropagation(); }));
        ['dragenter', 'dragover'].forEach(ev =>
            uploadZone.addEventListener(ev, () => uploadZone.classList.add('drag-active')));
        ['dragleave', 'drop'].forEach(ev =>
            uploadZone.addEventListener(ev, () => uploadZone.classList.remove('drag-active')));
        uploadZone.addEventListener('drop', e => handleFiles(e.dataTransfer.files));
        fileInput.addEventListener('change', function () { handleFiles(this.files); });

        // ── File handling ──
        function handleFiles(files) {
            if (!files.length) return;
            currentFiles = Array.from(files);
            uploadZone.style.display = 'none';
            convState.style.display = 'block';
            fileListCont.innerHTML = '';

            currentFiles.forEach((file, i) => {
                const mb = (file.size / 1048576).toFixed(2);
                const isPdf = file.type === 'application/pdf';
                const isImg = file.type.startsWith('image/');
                const isWord = /\.(doc|docx)$/i.test(file.name);
                const isXls = /\.(xls|xlsx)$/i.test(file.name);
                const isPpt = /\.(ppt|pptx)$/i.test(file.name);
                const icon = isPdf ? 'document-text' : isImg ? 'image' : isWord ? 'document-text' : isXls ? 'grid' : isPpt ? 'easel' : 'document';
                const color = isPdf ? '#ef4444' : isImg ? '#10b981' : isWord ? '#2b7cd3' : isXls ? '#107c41' : isPpt ? '#d24726' : '#6366f1';
                fileListCont.insertAdjacentHTML('beforeend', `
                    <div class="selected-file-item">
                        <div class="file-info-col">
                            <div class="file-icon" id="ficon${i}" style="color:${color};background:${color}18;">
                                <ion-icon name="${icon}"></ion-icon>
                            </div>
                            <div class="file-details"><h4>${file.name}</h4><p>${mb} MB</p></div>
                        </div>
                        <button class="remove-file-btn" onclick="resetUploader()">
                            <ion-icon name="close-outline"></ion-icon>
                        </button>
                    </div>`);
                if (isImg) {
                    const r = new FileReader();
                    r.onload = ev => { const d = document.getElementById(`ficon${i}`); if (d) { d.style.backgroundImage = `url(${ev.target.result})`; d.innerHTML = ''; } };
                    r.readAsDataURL(file);
                }
            });
        }

        // ── Reset ──
        window.resetUploader = function () {
            currentFiles = []; resultUrl = '';
            uploadZone.style.display = 'flex'; convState.style.display = 'none';
            fileInput.value = '';
            if (optBar) { optBar.style.display = 'flex'; }
            if (progCont) { progCont.style.display = 'none'; }
            if (succCont) { succCont.style.display = 'none'; }
            if (progBar) { progBar.style.width = '0%'; progBar.style.background = ''; progBar.style.boxShadow = ''; }
            if (progText) { progText.innerText = '0%'; }
            if (statusText) { statusText.innerText = 'Processing your file…'; statusText.style.color = ''; }
        };

        // ── Convert ──
        startBtn.addEventListener('click', async () => {
            if (!currentFiles.length) return;
            optBar.style.display = 'none';
            progCont.style.display = 'block';
            statusText.innerHTML = 'Uploading & converting<span class="typing-dot"></span><span class="typing-dot"></span><span class="typing-dot"></span>';
            animateProgress(progBar, progText, 18, 600);

            let fake = 18;
            const creep = setInterval(() => {
                if (fake < 82) { fake += Math.random() * 4; animateProgress(progBar, progText, Math.min(fake, 82), 900); }
            }, 1000);

            try {
                const fd = new FormData();
                currentFiles.forEach(f => fd.append('files', f));
                // Some ConvertAPI tools need additional params.
                if (toolId === 'protect-pdf') {
                    const pwd = (window.prompt('Enter a password to protect this PDF:') || '').trim();
                    if (!pwd) throw new Error('Password is required for Protect PDF.');
                    fd.append('UserPassword', pwd);
                } else if (toolId === 'unlock-pdf') {
                    const pwd = (window.prompt('Enter PDF password (leave blank if not needed):') || '').trim();
                    if (pwd) fd.append('Password', pwd);
                } else if (toolId === 'edit-pdf' || toolId === 'sign-pdf') {
                    const defaultText = toolId === 'sign-pdf' ? 'Signed via PDF2Pro' : 'Edited via PDF2Pro';
                    const label = toolId === 'sign-pdf' ? 'signature' : 'watermark';
                    const text = (window.prompt(`Enter ${label} text:`, defaultText) || '').trim();
                    if (!text) throw new Error('Text is required for this tool.');
                    fd.append('Text', text);
                }

                if (!location.origin || location.origin === 'null') {
                    throw new Error('Open this app via http://localhost:3000 (not file://).');
                }

                const res = await fetch(`${location.origin}/api/convert/${toolId}`, { method: 'POST', body: fd });
                clearInterval(creep);
                const data = await res.json().catch(() => ({}));

                if (!res.ok) {
                    const details = formatServerDetails(data.details);
                    const message = details ? `${data.error || 'Conversion failed.'} ${details}` : (data.error || `Request failed (${res.status})`);
                    throw new Error(message);
                }

                if (data.success && data.data?.Files?.length) {
                    resultUrl = data.data.Files[0].Url;
                    resultName = data.data.Files[0].FileName || `converted.${info.ext}`;
                    animateProgress(progBar, progText, 100, 500);
                    statusText.innerText = '✓ Conversion complete!';
                    setTimeout(() => { progCont.style.display = 'none'; showSuccess(); }, 650);
                } else {
                    const details = formatServerDetails(data.details);
                    throw new Error(details ? `${data.error || 'Conversion failed.'} ${details}` : (data.error || 'Conversion failed. Please try again.'));
                }
            } catch (err) {
                clearInterval(creep);
                progBar.style.width = '100%'; progBar.style.background = '#ef4444'; progBar.style.boxShadow = 'none';
                progText.innerText = 'Error';
                statusText.innerText = '⚠ ' + (err.message || 'Something went wrong.');
                statusText.style.color = '#ef4444';
                setTimeout(resetUploader, 3500);
            }
        });

        // ── Success state ──
        function showSuccess() {
            downloadBtn.href = resultUrl;
            downloadBtn.setAttribute('download', resultName);
            downloadBtn.onclick = null;
            previewBtn.onclick = () => openPreview(resultUrl, resultName);
            succCont.style.display = 'flex';
            // Bounce-in checkmark
            const ico = succCont.querySelector('.success-icon-wrap ion-icon');
            if (ico) {
                ico.style.transform = 'scale(0) rotate(-180deg)';
                ico.style.transition = 'transform .6s cubic-bezier(.34,1.56,.64,1)';
                requestAnimationFrame(() => { ico.style.transform = 'scale(1) rotate(0deg)'; });
            }
        }

        if (convAnotherBtn) convAnotherBtn.addEventListener('click', resetUploader);
    }

    // Run after DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
