// AI JobBot - Main Application JavaScript

// Job Search Handler
if (document.getElementById('job-search-form')) {
    document.getElementById('job-search-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const query = document.getElementById('search-query').value;
        const location = document.getElementById('search-location').value;
        
        try {
            const response = await fetch('/api/search-jobs', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query, location, limit: 20 })
            });
            
            const result = await response.json();
            
            if (result.success) {
                displayJobs(result.jobs);
                document.getElementById('results-count').textContent = result.count;
                document.getElementById('search-results').style.display = 'block';
                showToast(`Found ${result.count} jobs!`, 'success');
            } else {
                showToast('Search failed', 'error');
            }
        } catch (error) {
            showToast('Network error', 'error');
        }
    });
}

function displayJobs(jobs) {
    const container = document.getElementById('jobs-list');
    
    container.innerHTML = jobs.map(job => `
        <div class="job-card">
            <div class="job-header">
                <h3>${job.title}</h3>
                <span class="match-score">${job.match_score}% Match</span>
            </div>
            <p class="job-company">${job.company}</p>
            <p class="job-location">${job.location}</p>
            <p class="job-platform">via ${job.platform}</p>
            <div class="job-actions">
                <button onclick="applyToJob('${job.url}', '${job.platform}', ${JSON.stringify(job).replace(/'/g, "&apos;")})" class="btn btn-primary">Apply (1 Credit)</button>
                <a href="${job.url}" target="_blank" class="btn btn-secondary">View Job</a>
            </div>
        </div>
    `).join('');
}

async function applyToJob(url, platform, jobData) {
    if (!confirm('Apply to this job for 1 credit?')) return;
    
    try {
        const response = await fetch('/api/apply', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ job_url: url, platform, job_data: jobData })
        });
        
        const result = await response.json();
        
        if (result.status === 'captcha_required') {
            showCaptchaModal(result);
        } else if (result.status === 'success') {
            showToast('Application submitted!', 'success');
        } else {
            showToast(result.message || 'Application failed', 'error');
        }
    } catch (error) {
        showToast('Network error', 'error');
    }
}

function showCaptchaModal(result) {
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.innerHTML = `
        <div class="modal-content">
            <h2>Security Check Required</h2>
            <p>${result.instructions || 'Please complete the CAPTCHA in the browser window'}</p>
            <button onclick="this.closest('.modal').remove()" class="btn btn-primary">Done</button>
        </div>
    `;
    document.body.appendChild(modal);
}

// Cover Letter Generator
if (document.getElementById('letter-form')) {
    document.getElementById('letter-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const formData = new FormData(e.target);
        const jobInfo = {
            company: formData.get('company'),
            title: formData.get('title'),
            description: formData.get('description')
        };
        
        const btn = e.target.querySelector('button[type="submit"]');
        btn.disabled = true;
        btn.textContent = 'Generating...';
        
        try {
            const response = await fetch('/api/generate-letter', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ job_info: jobInfo })
            });
            
            const result = await response.json();
            
            if (result.success) {
                document.getElementById('letter-text').textContent = result.letter.text;
                document.getElementById('letter-output').style.display = 'block';
                showToast('Letter generated!', 'success');
            } else {
                showToast(result.error || 'Generation failed', 'error');
            }
        } catch (error) {
            showToast('Network error', 'error');
        } finally {
            btn.disabled = false;
            btn.textContent = 'Generate Letter (1 Credit)';
        }
    });
}

function downloadLetter() {
    const text = document.getElementById('letter-text').textContent;
    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'cover_letter.txt';
    a.click();
}
