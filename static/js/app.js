/**
 * Packing App - Main JavaScript
 * Handles AJAX interactions for the packing list app
 */

// CSRF token helper for Django
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

// Fetch wrapper with CSRF token
async function apiRequest(url, method = 'GET', data = null) {
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        credentials: 'same-origin',
    };
    
    if (data && method !== 'GET') {
        options.body = JSON.stringify(data);
    }
    
    const response = await fetch(url, options);
    
    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'An error occurred' }));
        throw new Error(error.detail || 'An error occurred');
    }
    
    if (response.status === 204) {
        return null;
    }
    
    return response.json();
}

// Toggle item packed status
async function toggleItemPacked(tripId, itemId, checkbox) {
    const isPacked = checkbox.checked;
    const listItem = checkbox.closest('.list-group-item');
    
    try {
        await apiRequest(`/api/trips/${tripId}/items/${itemId}/`, 'PATCH', {
            is_packed: isPacked
        });
        
        if (isPacked) {
            listItem.classList.add('item-packed');
        } else {
            listItem.classList.remove('item-packed');
        }
        
        // Update progress bar if present
        updateTripProgress(tripId);
    } catch (error) {
        // Revert checkbox on error
        checkbox.checked = !isPacked;
        showAlert('danger', error.message);
    }
}

// Update trip progress bar
function updateTripProgress(tripId) {
    const progressBar = document.querySelector(`[data-trip-progress="${tripId}"]`);
    if (!progressBar) return;
    
    // Find all item checkboxes within cards that have data-trip-id
    // Each category card and the custom items card have this attribute
    const tripCards = document.querySelectorAll(`[data-trip-id="${tripId}"]`);
    let total = 0;
    let packed = 0;
    
    tripCards.forEach(card => {
        const checkboxes = card.querySelectorAll('input[type="checkbox"]');
        checkboxes.forEach(cb => {
            total++;
            if (cb.checked) packed++;
        });
    });
    
    const percentage = total > 0 ? Math.round((packed / total) * 100) : 0;
    
    progressBar.style.width = `${percentage}%`;
    progressBar.setAttribute('aria-valuenow', percentage);
    progressBar.textContent = `${percentage}%`;
    
    // Update progress bar color based on completion
    if (percentage === 100) {
        progressBar.classList.add('bg-success');
    } else {
        progressBar.classList.remove('bg-success');
    }
    
    // Update counter if present
    const counter = document.querySelector(`[data-trip-counter="${tripId}"]`);
    if (counter) {
        counter.textContent = `${packed}/${total}`;
    }
}

// Show Bootstrap alert
function showAlert(type, message) {
    const alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    const container = document.querySelector('.container');
    if (container) {
        container.insertAdjacentHTML('afterbegin', alertHtml);
    }
}

// Delete confirmation
function confirmDelete(message) {
    return confirm(message || 'Are you sure you want to delete this item?');
}

// Add item to category inline
async function addItemToCategory(categoryId, itemName, listElement) {
    try {
        const item = await apiRequest(`/api/categories/${categoryId}/items/`, 'POST', {
            name: itemName
        });
        
        // Add item to the list
        const itemHtml = `
            <li class="list-group-item d-flex justify-content-between align-items-center" data-item-id="${item.id}">
                <span>${item.name}</span>
                <button type="button" class="btn btn-sm btn-outline-danger" onclick="deleteItem(${categoryId}, ${item.id}, this)">
                    <i class="bi bi-trash"></i>
                </button>
            </li>
        `;
        listElement.insertAdjacentHTML('beforeend', itemHtml);
        
        return item;
    } catch (error) {
        showAlert('danger', error.message);
        throw error;
    }
}

// Delete item from category
async function deleteItem(categoryId, itemId, button) {
    if (!confirmDelete('Are you sure you want to delete this item?')) {
        return;
    }
    
    try {
        await apiRequest(`/api/categories/${categoryId}/items/${itemId}/`, 'DELETE');
        
        const listItem = button.closest('.list-group-item');
        listItem.remove();
    } catch (error) {
        showAlert('danger', error.message);
    }
}

// Add item to trip
async function addItemToTrip(tripId, itemName, categoryId = null) {
    try {
        const data = { name: itemName };
        if (categoryId) {
            data.source_category = categoryId;
        }
        
        const item = await apiRequest(`/api/trips/${tripId}/items/`, 'POST', data);
        return item;
    } catch (error) {
        showAlert('danger', error.message);
        throw error;
    }
}

// Delete category
async function deleteCategory(categoryId, element) {
    if (!confirmDelete('Are you sure you want to delete this category and all its items?')) {
        return;
    }
    
    try {
        await apiRequest(`/api/categories/${categoryId}/`, 'DELETE');
        
        const card = element.closest('.accordion-item') || element.closest('.card');
        if (card) {
            card.remove();
        }
    } catch (error) {
        showAlert('danger', error.message);
    }
}

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
});
