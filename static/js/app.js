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
            if (cookie.substring(0, name.length + 1) === `${name}=`) {
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
            is_packed: isPacked,
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

    tripCards.forEach((card) => {
        const checkboxes = card.querySelectorAll('input[type="checkbox"]');
        checkboxes.forEach((cb) => {
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
            name: itemName,
        });

        // Add item to the list
        const itemHtml = `
            <li class="list-group-item d-flex justify-content-between align-items-center" data-item-id="${item.id}">
                <span class="item-name">${item.name}</span>
                <div class="btn-group btn-group-sm">
                    <button type="button" class="btn btn-sm btn-outline-secondary edit-icon" 
                            onclick="editCategoryItem(${categoryId}, ${item.id}, this)"
                            title="Edit item">
                        <i class="bi bi-pencil"></i>
                    </button>
                    <button type="button" class="btn btn-sm btn-outline-danger" onclick="deleteItem(${categoryId}, ${item.id}, this)">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
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

// ============================================
// Inline Editing Functions
// ============================================

/**
 * Create an inline edit input that replaces a text element
 * @param {HTMLElement} textElement - The element containing the text to edit
 * @param {string} currentValue - The current text value
 * @param {Function} onSave - Callback when save is triggered (receives new value)
 * @returns {HTMLInputElement} The created input element
 */
function createInlineEdit(textElement, currentValue, onSave) {
    const input = document.createElement('input');
    input.type = 'text';
    input.className = 'form-control form-control-sm inline-edit-input';
    input.value = currentValue;

    // Store original display for restoration
    const originalDisplay = textElement.style.display;
    textElement.style.display = 'none';
    textElement.parentNode.insertBefore(input, textElement.nextSibling);
    input.focus();
    input.select();

    let saved = false;

    const save = async () => {
        if (saved) return;
        saved = true;

        const newValue = input.value.trim();
        if (newValue && newValue !== currentValue) {
            try {
                await onSave(newValue);
                textElement.textContent = newValue;
            } catch (error) {
                // Restore on error
                showAlert('danger', error.message);
            }
        }
        cleanup();
    };

    const cancel = () => {
        if (saved) return;
        saved = true;
        cleanup();
    };

    const cleanup = () => {
        textElement.style.display = originalDisplay;
        input.remove();
    };

    input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            save();
        } else if (e.key === 'Escape') {
            e.preventDefault();
            cancel();
        }
    });

    input.addEventListener('blur', () => {
        // Small delay to allow click events to register
        setTimeout(() => {
            if (!saved) save();
        }, 100);
    });

    return input;
}

// Edit category name
function editCategory(categoryId, button) {
    const card = button.closest('.card');
    const nameElement = card.querySelector('.category-name');
    const currentName = nameElement.textContent.trim();

    createInlineEdit(nameElement, currentName, async (newName) => {
        await apiRequest(`/api/categories/${categoryId}/`, 'PATCH', { name: newName });
    });
}

// Edit trip name
function editTripName(tripId, button) {
    const nameElement = document.querySelector('.trip-name');
    const currentName = nameElement.textContent.trim();

    createInlineEdit(nameElement, currentName, async (newName) => {
        await apiRequest(`/api/trips/${tripId}/`, 'PATCH', { name: newName });
        // Also update the breadcrumb
        const breadcrumb = document.querySelector('.trip-name-breadcrumb');
        if (breadcrumb) {
            breadcrumb.textContent = newName;
        }
        // Update the page title
        document.title = `${newName} - Packing App`;
    });
}

// Edit category item name
function editCategoryItem(categoryId, itemId, button) {
    const listItem = button.closest('.list-group-item');
    const nameElement = listItem.querySelector('.item-name');
    const currentName = nameElement.textContent.trim();

    createInlineEdit(nameElement, currentName, async (newName) => {
        await apiRequest(`/api/categories/${categoryId}/items/${itemId}/`, 'PATCH', {
            name: newName,
        });
    });
}

// Edit trip item name
function editTripItem(tripId, itemId, button) {
    const listItem = button.closest('.list-group-item');
    const label = listItem.querySelector('.form-check-label');
    const nameElement = label.querySelector('.item-name');
    const currentName = nameElement.textContent.trim();

    createInlineEdit(nameElement, currentName, async (newName) => {
        await apiRequest(`/api/trips/${tripId}/items/${itemId}/`, 'PATCH', { name: newName });
    });
}

// Delete trip item
async function deleteTripItem(tripId, itemId, button) {
    if (!confirmDelete('Remove this item from the trip?')) {
        return;
    }

    try {
        await apiRequest(`/api/trips/${tripId}/items/${itemId}/`, 'DELETE');

        const listItem = button.closest('.list-group-item');
        listItem.remove();

        // Update progress bar
        updateTripProgress(tripId);
    } catch (error) {
        showAlert('danger', error.message);
    }
}

// Initialize "Select All" checkbox for category selection (trip create page)
function initSelectAllCategories() {
    const selectAllCheckbox = document.getElementById('select-all-categories');
    const categoryCheckboxes = document.querySelectorAll('input[name="categories"]');

    if (selectAllCheckbox && categoryCheckboxes.length > 0) {
        // Update "Select All" checkbox state based on individual checkboxes
        function updateSelectAllState() {
            const allChecked = Array.from(categoryCheckboxes).every((cb) => cb.checked);
            const someChecked = Array.from(categoryCheckboxes).some((cb) => cb.checked);
            selectAllCheckbox.checked = allChecked;
            selectAllCheckbox.indeterminate = someChecked && !allChecked;
        }

        // Toggle all checkboxes when "Select All" is clicked
        selectAllCheckbox.addEventListener('change', function () {
            const isChecked = this.checked;
            categoryCheckboxes.forEach((cb) => {
                cb.checked = isChecked;
            });
        });

        // Update "Select All" state when individual checkboxes change
        categoryCheckboxes.forEach((cb) => {
            cb.addEventListener('change', updateSelectAllState);
        });

        // Set initial state
        updateSelectAllState();
    }
}

// Initialize page
document.addEventListener('DOMContentLoaded', () => {
    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach((alert) => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Initialize select all categories (trip create page)
    initSelectAllCategories();
});
