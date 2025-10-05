// BUDUN Sigorta Web Sitesi - JavaScript Functions

// Global variables
let currentUser = null;
let policies = [];
let salespeople = [];

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

// Initialize application
function initializeApp() {
    // Check if user is logged in
    checkAuthStatus();
    
    // Initialize tooltips
    initializeTooltips();
    
    // Initialize form validations
    initializeFormValidations();
    
    // Load initial data
    loadInitialData();
}

// Check authentication status
function checkAuthStatus() {
    // This would typically check session or token
    console.log('Authentication status checked');
}

// Initialize Bootstrap tooltips
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Initialize form validations
function initializeFormValidations() {
    // Custom form validation
    const forms = document.querySelectorAll('.needs-validation');
    
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
}

// Load initial data
async function loadInitialData() {
    try {
        // Load policies if on policies page
        if (window.location.pathname.includes('policies')) {
            await loadPolicies();
        }
        
        // Load salespeople if needed
        if (document.getElementById('salespersonSelect')) {
            await loadSalespeople();
        }
        
    } catch (error) {
        console.error('Initial data loading error:', error);
        showNotification('Veriler yüklenirken hata oluştu!', 'error');
    }
}

// Load policies data
async function loadPolicies() {
    try {
        const response = await fetch('/api/policies');
        const data = await response.json();
        
        if (data.policies) {
            policies = data.policies;
            updatePoliciesTable(policies);
        }
    } catch (error) {
        console.error('Policies loading error:', error);
    }
}

// Load salespeople data
async function loadSalespeople() {
    try {
        const response = await fetch('/api/salespeople');
        const data = await response.json();
        
        if (data.salespeople) {
            salespeople = data.salespeople;
            updateSalespeopleSelect(salespeople);
        }
    } catch (error) {
        console.error('Salespeople loading error:', error);
    }
}

// Update policies table
function updatePoliciesTable(policiesData) {
    const tbody = document.getElementById('policiesTable');
    if (!tbody) return;
    
    if (policiesData.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="10" class="text-center text-muted">
                    <i class="fas fa-inbox me-2"></i>Henüz poliçe bulunmuyor
                </td>
            </tr>
        `;
        return;
    }
    
    tbody.innerHTML = policiesData.map(policy => `
        <tr>
            <td><strong>${policy.policy_number || '-'}</strong></td>
            <td>${policy.customer_name || '-'}</td>
            <td>${policy.customer_tc || '-'}</td>
            <td>${policy.plate_number || '-'}</td>
            <td><span class="badge bg-secondary">${policy.product || '-'}</span></td>
            <td>${policy.insurance_company || '-'}</td>
            <td>${policy.salesperson || '-'}</td>
            <td><strong>₺${formatNumber(policy.gross_premium || 0)}</strong></td>
            <td>${formatDate(policy.end_date)}</td>
            <td>
                <button class="btn btn-sm btn-outline-primary me-1" onclick="viewPolicy(${policy.id})" title="Görüntüle">
                    <i class="fas fa-eye"></i>
                </button>
                <button class="btn btn-sm btn-outline-warning" onclick="editPolicy(${policy.id})" title="Düzenle">
                    <i class="fas fa-edit"></i>
                </button>
            </td>
        </tr>
    `).join('');
}

// Update salespeople select
function updateSalespeopleSelect(salespeopleData) {
    const select = document.getElementById('salespersonSelect');
    if (!select) return;
    
    select.innerHTML = '<option value="">Seçiniz</option>';
    
    salespeopleData.forEach(salesperson => {
        const option = document.createElement('option');
        option.value = salesperson.name;
        option.textContent = salesperson.name;
        select.appendChild(option);
    });
}

// Format number for Turkish locale
function formatNumber(number) {
    return new Intl.NumberFormat('tr-TR').format(number);
}

// Format date for Turkish locale
function formatDate(dateString) {
    if (!dateString) return '-';
    
    try {
        const date = new Date(dateString);
        return date.toLocaleDateString('tr-TR');
    } catch (error) {
        return dateString;
    }
}

// Show notification
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    
    notification.innerHTML = `
        <i class="fas fa-${type === 'error' ? 'exclamation-triangle' : 'info-circle'} me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Add to body
    document.body.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 5000);
}

// Search functionality
function searchPolicies(searchTerm) {
    if (!searchTerm) {
        updatePoliciesTable(policies);
        return;
    }
    
    const filtered = policies.filter(policy => 
        (policy.policy_number && policy.policy_number.toLowerCase().includes(searchTerm.toLowerCase())) ||
        (policy.customer_name && policy.customer_name.toLowerCase().includes(searchTerm.toLowerCase())) ||
        (policy.customer_tc && policy.customer_tc.includes(searchTerm)) ||
        (policy.plate_number && policy.plate_number.toLowerCase().includes(searchTerm.toLowerCase()))
    );
    
    updatePoliciesTable(filtered);
}

// Filter policies
function filterPolicies() {
    const productFilter = document.getElementById('productFilter')?.value;
    const statusFilter = document.getElementById('statusFilter')?.value;
    
    let filtered = [...policies];
    
    // Filter by product
    if (productFilter) {
        filtered = filtered.filter(policy => policy.product === productFilter);
    }
    
    // Filter by status
    if (statusFilter) {
        const now = new Date();
        const thirtyDaysFromNow = new Date();
        thirtyDaysFromNow.setDate(now.getDate() + 30);
        
        filtered = filtered.filter(policy => {
            if (!policy.end_date) return false;
            
            const endDate = new Date(policy.end_date);
            
            switch (statusFilter) {
                case 'active':
                    return endDate > now;
                case 'expiring':
                    return endDate <= thirtyDaysFromNow && endDate > now;
                case 'expired':
                    return endDate <= now;
                default:
                    return true;
            }
        });
    }
    
    updatePoliciesTable(filtered);
}

// Clear all filters
function clearFilters() {
    const searchInput = document.getElementById('searchInput');
    const productFilter = document.getElementById('productFilter');
    const statusFilter = document.getElementById('statusFilter');
    
    if (searchInput) searchInput.value = '';
    if (productFilter) productFilter.value = '';
    if (statusFilter) statusFilter.value = '';
    
    updatePoliciesTable(policies);
}

// Add policy
async function addPolicy(formData) {
    try {
        const response = await fetch('/api/policies', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showNotification('Poliçe başarıyla eklendi!', 'success');
            await loadPolicies(); // Reload policies
            return true;
        } else {
            showNotification('Hata: ' + result.error, 'error');
            return false;
        }
    } catch (error) {
        console.error('Add policy error:', error);
        showNotification('Poliçe eklenirken hata oluştu!', 'error');
        return false;
    }
}

// View policy details
function viewPolicy(id) {
    // This would open a modal or navigate to policy details
    showNotification('Poliçe görüntüleme özelliği yakında eklenecek!', 'info');
}

// Edit policy
function editPolicy(id) {
    // This would open edit modal or navigate to edit page
    showNotification('Poliçe düzenleme özelliği yakında eklenecek!', 'info');
}

// Export data
function exportData(format = 'excel') {
    showNotification(`${format.toUpperCase()} export özelliği yakında eklenecek!`, 'info');
}

// Print report
function printReport() {
    window.print();
}

// Utility functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Initialize search with debounce
const debouncedSearch = debounce(searchPolicies, 300);

// Add event listeners
document.addEventListener('DOMContentLoaded', function() {
    // Search input
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', function(e) {
            debouncedSearch(e.target.value);
        });
    }
    
    // Filter selects
    const productFilter = document.getElementById('productFilter');
    const statusFilter = document.getElementById('statusFilter');
    
    if (productFilter) {
        productFilter.addEventListener('change', filterPolicies);
    }
    
    if (statusFilter) {
        statusFilter.addEventListener('change', filterPolicies);
    }
});
