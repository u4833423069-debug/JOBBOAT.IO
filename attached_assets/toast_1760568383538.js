// Toast notification system
function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container') || createToastContainer();
    
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    
    container.appendChild(toast);
    
    setTimeout(() => toast.classList.add('show'), 10);
    
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.style.cssText = 'position:fixed;top:20px;right:20px;z-index:10000;';
    document.body.appendChild(container);
    
    const style = document.createElement('style');
    style.textContent = `
        .toast {
            padding: 1rem 1.5rem;
            margin-bottom: 0.5rem;
            border-radius: 8px;
            color: white;
            opacity: 0;
            transform: translateX(100%);
            transition: all 0.3s ease;
            min-width: 250px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        }
        .toast.show { opacity: 1; transform: translateX(0); }
        .toast-success { background: #00FF88; color: #0A0E27; }
        .toast-error { background: #E53E3E; }
        .toast-info { background: #00F0FF; color: #0A0E27; }
    `;
    document.head.appendChild(style);
    
    return container;
}
