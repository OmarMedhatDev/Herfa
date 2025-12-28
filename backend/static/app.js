// Herfa Marketplace - Frontend Application
const API_BASE = 'http://localhost:8000/api';
let currentUser = null;
let currentToken = localStorage.getItem('herfa_token') || null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    if (currentToken) {
        loadUserInfo();
    } else {
        showAuth();
    }
});

// API Helper
async function apiCall(endpoint, method = 'GET', body = null) {
    const options = {
        method,
        headers: { 'Content-Type': 'application/json' }
    };

    if (currentToken) {
        options.headers['Authorization'] = `Bearer ${currentToken}`;
    }

    if (body) {
        options.body = JSON.stringify(body);
    }

    try {
        const response = await fetch(`${API_BASE}${endpoint}`, options);
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || data.detail || Object.values(data)[0]?.[0] || 'Request failed');
        }
        
        // Handle paginated responses (Django REST Framework pagination)
        if (data.results !== undefined) {
            return data.results;
        }
        
        return data;
    } catch (error) {
        console.error('API Error:', error);
        showMessage(error.message, 'error');
        throw error;
    }
}

// Message Display
function showMessage(text, type = 'success') {
    const container = document.getElementById('messageContainer');
    const icon = type === 'error' ? 'exclamation-circle' : type === 'info' ? 'info-circle' : 'check-circle';
    container.innerHTML = `
        <div class="message message-${type}">
            <i class="fas fa-${icon}"></i>
            <span>${text}</span>
        </div>
    `;
    setTimeout(() => container.innerHTML = '', 5000);
}

// Authentication
async function handleLogin(e) {
    e.preventDefault();
    const username = document.getElementById('loginUsername').value;
    const password = document.getElementById('loginPassword').value;
    
    try {
        const data = await apiCall('/auth/login/', 'POST', { username, password });
        currentToken = data.tokens.access;
        localStorage.setItem('herfa_token', currentToken);
        showMessage('Login successful!');
        await loadUserInfo();
    } catch (error) {
        // Error already shown
    }
}

async function quickLogin(username, password) {
    try {
        const data = await apiCall('/auth/login/', 'POST', { username, password });
        currentToken = data.tokens.access;
        localStorage.setItem('herfa_token', currentToken);
        showMessage(`Logged in as ${username}!`);
        await loadUserInfo();
    } catch (error) {
        // Error already shown
    }
}

async function handleRegister(e) {
    e.preventDefault();
    const data = {
        username: document.getElementById('regUsername').value,
        email: document.getElementById('regEmail').value,
        password: document.getElementById('regPassword').value,
        password2: document.getElementById('regPassword2').value,
        role: document.getElementById('regRole').value
    };

    if (data.password !== data.password2) {
        showMessage('Passwords do not match', 'error');
        return;
    }

    try {
        const result = await apiCall('/auth/register/', 'POST', data);
        currentToken = result.tokens.access;
        localStorage.setItem('herfa_token', currentToken);
        showMessage('Registration successful!');
        await loadUserInfo();
    } catch (error) {
        // Error already shown
    }
}

function logout() {
    currentToken = null;
    currentUser = null;
    localStorage.removeItem('herfa_token');
    showAuth();
    showMessage('Logged out successfully');
}

// User Info
async function loadUserInfo() {
    try {
        const profile = await apiCall('/profiles/me/');
        currentUser = profile;
        
        // Update header
        document.getElementById('headerAuth').classList.add('hidden');
        document.getElementById('headerUser').classList.remove('hidden');
        document.getElementById('userName').textContent = profile.user?.username || profile.display_name;
        document.getElementById('userRole').textContent = profile.user?.role || 'USER';
        
        // Show navigation
        document.getElementById('navTabs').classList.remove('hidden');
        document.getElementById('authSection').classList.add('hidden');
        
        // Hide role-specific tabs
        const role = profile.user?.role;
        if (role === 'CLIENT') {
            document.getElementById('navOffers').style.display = 'none';
        } else if (role === 'ARTISAN') {
            document.getElementById('createRequestBtn').style.display = 'none';
        }
        
        showTab('dashboard');
        await loadDashboard();
    } catch (error) {
        showMessage('Failed to load user info', 'error');
        logout();
    }
}

// Navigation
function showAuth() {
    document.getElementById('headerAuth').classList.remove('hidden');
    document.getElementById('headerUser').classList.add('hidden');
    document.getElementById('navTabs').classList.add('hidden');
    document.getElementById('authSection').classList.remove('hidden');
    document.querySelectorAll('[id$="Tab"]').forEach(tab => tab.classList.add('hidden'));
}

function showTab(tabName) {
    document.querySelectorAll('.nav-tab').forEach(tab => tab.classList.remove('active'));
    document.querySelectorAll('[id$="Tab"]').forEach(tab => tab.classList.add('hidden'));
    
    event?.target?.classList.add('active');
    document.getElementById(`${tabName}Tab`).classList.remove('hidden');
    
    switch(tabName) {
        case 'dashboard': loadDashboard(); break;
        case 'requests': loadRequests(); break;
        case 'offers': loadOffers(); break;
        case 'wallet': loadWallet(); break;
        case 'profile': loadProfile(); break;
    }
}

function switchAuthTab(tab) {
    document.querySelectorAll('.auth-tab').forEach(t => t.classList.remove('active'));
    document.getElementById('loginForm').classList.toggle('hidden', tab !== 'login');
    document.getElementById('registerForm').classList.toggle('hidden', tab !== 'register');
    event.target.classList.add('active');
}

// Dashboard
async function loadDashboard() {
    const statsDiv = document.getElementById('dashboardStats');
    const activityDiv = document.getElementById('dashboardActivity');
    
    try {
        const role = currentUser?.user?.role;
        
        // Load wallet
        try {
            const wallet = await apiCall('/payments/wallet/');
            document.getElementById('dashboardBalance').textContent = `${wallet.balance} EGP`;
        } catch (error) {
            document.getElementById('dashboardBalance').textContent = '0.00 EGP';
        }
        
        // Load requests
        let requests = [];
        try {
            requests = await apiCall('/requests/');
            // Ensure it's an array
            if (!Array.isArray(requests)) {
                requests = [];
            }
        } catch (error) {
            requests = [];
        }
        
        const stats = {
            totalRequests: requests.length,
            openRequests: requests.filter(r => r.status === 'OPEN').length,
            inProgress: requests.filter(r => r.status === 'IN_PROGRESS').length,
            completed: requests.filter(r => r.status === 'COMPLETED').length
        };
        
        statsDiv.innerHTML = `
            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px;">
                <div style="text-align: center; padding: 15px; background: #f3f4f6; border-radius: 10px;">
                    <div style="font-size: 32px; font-weight: 700; color: var(--primary);">${stats.totalRequests}</div>
                    <div style="color: var(--gray); font-size: 14px;">Total Requests</div>
                </div>
                <div style="text-align: center; padding: 15px; background: #f3f4f6; border-radius: 10px;">
                    <div style="font-size: 32px; font-weight: 700; color: var(--success);">${stats.openRequests}</div>
                    <div style="color: var(--gray); font-size: 14px;">Open</div>
                </div>
                <div style="text-align: center; padding: 15px; background: #f3f4f6; border-radius: 10px;">
                    <div style="font-size: 32px; font-weight: 700; color: var(--warning);">${stats.inProgress}</div>
                    <div style="color: var(--gray); font-size: 14px;">In Progress</div>
                </div>
                <div style="text-align: center; padding: 15px; background: #f3f4f6; border-radius: 10px;">
                    <div style="font-size: 32px; font-weight: 700; color: var(--gray);">${stats.completed}</div>
                    <div style="color: var(--gray); font-size: 14px;">Completed</div>
                </div>
            </div>
        `;
        
        activityDiv.innerHTML = requests.slice(0, 5).map(req => `
            <div style="padding: 15px; border-bottom: 1px solid #e5e7eb; display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <strong>${req.category}</strong>
                    <span class="status-badge status-${req.status.toLowerCase().replace('_', '-')}">${req.status}</span>
                    <div style="color: var(--gray); font-size: 13px; margin-top: 5px;">${req.description.substring(0, 50)}...</div>
                </div>
                <div style="color: var(--gray); font-size: 12px;">${new Date(req.created_at).toLocaleDateString()}</div>
            </div>
        `).join('') || '<p style="text-align: center; color: var(--gray); padding: 20px;">No recent activity</p>';
    } catch (error) {
        statsDiv.innerHTML = '<p style="color: var(--danger);">Failed to load statistics</p>';
    }
}

// Service Requests
async function loadRequests() {
    const listDiv = document.getElementById('requestsList');
    listDiv.innerHTML = '<div class="loading"><div class="spinner"></div><p>Loading requests...</p></div>';
    
    try {
        let requests = await apiCall('/requests/');
        
        // Ensure it's an array
        if (!Array.isArray(requests)) {
            requests = [];
        }
        
        if (requests.length === 0) {
            listDiv.innerHTML = '<p style="text-align: center; color: var(--gray); padding: 40px;">No service requests found.</p>';
            return;
        }
        
        listDiv.innerHTML = requests.map(req => `
            <div class="request-card">
                <div class="request-header">
                    <span class="request-category">${req.category}</span>
                    <span class="status-badge status-${req.status.toLowerCase().replace('_', '-')}">${req.status}</span>
                </div>
                <div class="request-body">
                    <div class="request-description">${req.description}</div>
                    <div class="request-meta">
                        <span><i class="fas fa-money-bill-wave"></i> ${req.budget_min} - ${req.budget_max} EGP</span>
                        ${req.ai_suggested_price ? `<span><i class="fas fa-robot"></i> ${req.ai_suggested_price}</span>` : ''}
                        ${req.offers_count > 0 ? `<span><i class="fas fa-handshake"></i> ${req.offers_count} offers</span>` : ''}
                    </div>
                </div>
                <div class="request-actions">
                    ${currentUser?.user?.role === 'ARTISAN' && req.status === 'OPEN' ? 
                        `<button class="btn btn-success" onclick="openOfferModal('${req.id}')">
                            <i class="fas fa-paper-plane"></i> Submit Offer
                        </button>` : ''}
                    ${currentUser?.user?.role === 'CLIENT' && req.status === 'OPEN' && req.offers_count > 0 ?
                        `<button class="btn btn-primary" onclick="viewOffers('${req.id}')">
                            <i class="fas fa-eye"></i> View Offers
                        </button>` : ''}
                </div>
            </div>
        `).join('');
    } catch (error) {
        listDiv.innerHTML = '<p style="color: var(--danger);">Failed to load requests</p>';
    }
}

async function handleCreateRequest(e) {
    e.preventDefault();
    try {
        await apiCall('/requests/', 'POST', {
            category: document.getElementById('modalCategory').value,
            description: document.getElementById('modalDescription').value,
            budget_min: document.getElementById('modalBudgetMin').value,
            budget_max: document.getElementById('modalBudgetMax').value
        });
        showMessage('Service request created successfully!');
        closeModal('createRequestModal');
        document.getElementById('createRequestModal').querySelector('form').reset();
        loadRequests();
    } catch (error) {
        // Error already shown
    }
}

function showCreateRequestModal() {
    if (currentUser?.user?.role !== 'CLIENT') {
        showMessage('Only clients can create requests', 'error');
        return;
    }
    document.getElementById('createRequestModal').classList.add('active');
}

// Offers
async function loadOffers() {
    const listDiv = document.getElementById('offersList');
    listDiv.innerHTML = '<div class="loading"><div class="spinner"></div><p>Loading offers...</p></div>';
    
    try {
        let requests = await apiCall('/requests/');
        
        // Ensure it's an array
        if (!Array.isArray(requests)) {
            requests = [];
        }
        
        const offers = [];
        
        for (const req of requests) {
            if (req.offers && req.offers.length > 0) {
                offers.push(...req.offers.map(offer => ({ ...offer, request: req })));
            }
        }
        
        if (offers.length === 0) {
            listDiv.innerHTML = '<p style="text-align: center; color: var(--gray); padding: 40px;">No offers found.</p>';
            return;
        }
        
        listDiv.innerHTML = offers.map(offer => `
            <div class="offer-card">
                <div class="request-header">
                    <span class="request-category">${offer.request.category}</span>
                    <span class="status-badge status-${offer.status.toLowerCase()}">${offer.status}</span>
                </div>
                <div class="offer-price">${offer.price} EGP</div>
                <div class="request-description">${offer.message || 'No message'}</div>
                <div class="request-meta">
                    <span><i class="fas fa-user"></i> ${offer.artisan?.username || 'Artisan'}</span>
                    <span><i class="fas fa-calendar"></i> ${new Date(offer.created_at).toLocaleDateString()}</span>
                </div>
                ${currentUser?.user?.role === 'CLIENT' && offer.status === 'PENDING' ?
                    `<div class="request-actions">
                        <button class="btn btn-success" onclick="acceptOffer('${offer.id}')">
                            <i class="fas fa-check"></i> Accept Offer
                        </button>
                    </div>` : ''}
            </div>
        `).join('');
    } catch (error) {
        listDiv.innerHTML = '<p style="color: var(--danger);">Failed to load offers</p>';
    }
}

async function openOfferModal(requestId) {
    document.getElementById('offerRequestId').value = requestId;
    document.getElementById('offerModal').classList.add('active');
}

async function handleSubmitOffer(e) {
    e.preventDefault();
    try {
        const requestId = document.getElementById('offerRequestId').value;
        await apiCall(`/requests/${requestId}/bid/`, 'POST', {
            price: document.getElementById('offerPrice').value,
            message: document.getElementById('offerMessage').value
        });
        showMessage('Offer submitted successfully!');
        closeModal('offerModal');
        document.getElementById('offerModal').querySelector('form').reset();
        loadRequests();
    } catch (error) {
        // Error already shown
    }
}

async function acceptOffer(offerId) {
    if (!confirm('Accept this offer? Funds will be moved to escrow.')) return;
    
    try {
        await apiCall(`/offers/${offerId}/accept/`, 'POST');
        showMessage('Offer accepted! Funds moved to escrow.');
        loadOffers();
        loadRequests();
        loadDashboard();
    } catch (error) {
        // Error already shown
    }
}

// Wallet
async function loadWallet() {
    try {
        const wallet = await apiCall('/payments/wallet/');
        document.getElementById('walletBalance').textContent = `${wallet.balance} EGP`;
        
        let transactions = await apiCall('/payments/transactions/');
        
        // Ensure it's an array
        if (!Array.isArray(transactions)) {
            transactions = [];
        }
        
        const transactionsDiv = document.getElementById('transactionsList');
        
        if (transactions.length === 0) {
            transactionsDiv.innerHTML = '<p style="text-align: center; color: var(--gray); padding: 20px;">No transactions yet.</p>';
            return;
        }
        
        transactionsDiv.innerHTML = transactions.slice(0, 10).map(txn => `
            <div style="padding: 15px; border-bottom: 1px solid #e5e7eb; display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <strong>${txn.transaction_type.replace('_', ' ')}</strong>
                    <div style="color: var(--gray); font-size: 13px; margin-top: 5px;">${txn.description || ''}</div>
                </div>
                <div style="font-size: 18px; font-weight: 700; color: ${parseFloat(txn.amount) >= 0 ? 'var(--success)' : 'var(--danger)'};">
                    ${parseFloat(txn.amount) >= 0 ? '+' : ''}${txn.amount} EGP
                </div>
            </div>
        `).join('');
    } catch (error) {
        showMessage('Failed to load wallet', 'error');
    }
}

async function handleDeposit(e) {
    e.preventDefault();
    const amount = document.getElementById('depositAmount').value;
    
    try {
        await apiCall('/payments/deposit/', 'POST', { amount: parseFloat(amount) });
        showMessage(`Deposited ${amount} EGP successfully!`);
        document.getElementById('depositAmount').value = '';
        loadWallet();
        loadDashboard();
    } catch (error) {
        // Error already shown
    }
}

// Profile
async function loadProfile() {
    const contentDiv = document.getElementById('profileContent');
    
    try {
        const profile = await apiCall('/profiles/me/');
        const role = profile.user?.role;
        
        contentDiv.innerHTML = `
            <div class="profile-card">
                <div class="profile-avatar">${(profile.user?.username || profile.display_name || 'U')[0].toUpperCase()}</div>
                <div class="profile-info">
                    <h3>
                        ${profile.display_name || profile.user?.username}
                        ${role === 'ARTISAN' && profile.is_verified ? 
                            '<span class="verified-badge"><i class="fas fa-check-circle"></i> Verified</span>' : ''}
                    </h3>
                    <p><i class="fas fa-envelope"></i> ${profile.user?.email || 'N/A'}</p>
                    <p><i class="fas fa-user-tag"></i> ${role || 'USER'}</p>
                    ${profile.bio ? `<p style="margin-top: 10px;">${profile.bio}</p>` : ''}
                    ${profile.address ? `<p><i class="fas fa-map-marker-alt"></i> ${profile.address}</p>` : ''}
                    ${role === 'ARTISAN' ? `
                        <p style="margin-top: 15px;">
                            <strong>Verification Status:</strong> 
                            <span class="status-badge status-${profile.verification_status?.toLowerCase().replace('_', '-')}">
                                ${profile.verification_status}
                            </span>
                        </p>
                        ${profile.rating_avg > 0 ? `<p><strong>Rating:</strong> ${profile.rating_avg.toFixed(1)} ⭐</p>` : ''}
                    ` : ''}
                </div>
            </div>
        `;
    } catch (error) {
        contentDiv.innerHTML = '<p style="color: var(--danger);">Failed to load profile</p>';
    }
}

// Modal
function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('active');
}

// Close modal on outside click
document.querySelectorAll('.modal').forEach(modal => {
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.classList.remove('active');
        }
    });
});

