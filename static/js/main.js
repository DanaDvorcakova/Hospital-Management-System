document.addEventListener('DOMContentLoaded', function () {
    console.log("All scripts loaded!");

    // Initialize Table Search for various tables
    enableTableSearch('doctorSearch', [1, 2, 3]); // Doctor table search
    enableTableSearch('patientSearch', [1, 2, 3, 4]); // Patient table search
    enableTableSearch('appointmentsSearch', [0, 1, 2, 3, 4]); // Appointments table search
    enableTableSearch('recordsSearch', [0, 1, 2, 3, 4]); // Medical record search
    enableTableSearch('auditLogSearch', [0, 1, 2, 3, 4]); // Audit Log search

    // Initialize Appointment Chart
    loadAppointmentChart();

    // Initialize Modal Confirmations
    initModalConfirmations();
});

// ==========================
// Table Search Function 
// ==========================
function enableTableSearch(inputId, columnIndexes) {
    const searchInput = document.getElementById(inputId);
    if (!searchInput) return; 

    const rows = document.querySelectorAll('table tbody tr');

    searchInput.addEventListener('keyup', function () {
        const filter = this.value.toLowerCase();

        rows.forEach(row => {
            let matchFound = false;

            columnIndexes.forEach(index => {
                const cell = row.cells[index];
                if (!cell) return;

                // Store original text once if not already stored
                if (!cell.dataset.original) {
                    cell.dataset.original = cell.textContent.trim();
                }

                const originalText = cell.dataset.original.toLowerCase();
                
                if (filter && originalText.includes(filter)) {
                    matchFound = true;
                    // Highlight the matched term using a regex
                    const highlightedText = originalText.replace(
                        new RegExp(`(${filter})`, 'gi'),
                        '<mark>$1</mark>'
                    );
                    cell.innerHTML = highlightedText; // Only modify the text content when there's a match
                } else {
                    cell.innerHTML = cell.dataset.original; // Reset to the original text if no match
                }
            });
    
            // Show row if match is found or if search filter is empty
            row.style.display = matchFound || filter === '' ? '' : 'none';
        });
    });
}

// ==========================
// Table Filter Script
// ==========================
let activeFilters = {}; // Global active filters for all columns

function applyFilters() {
    const rows = document.querySelectorAll('#auditTable tbody tr');
    
    rows.forEach(row => {
        let shouldDisplay = true;
        
        // Check each filter for every row
        Object.keys(activeFilters).forEach(colIndex => {
            const cell = row.cells[colIndex];
            if (!cell) return;

            const cellText = cell.textContent.toLowerCase();
            if (!activeFilters[colIndex].includes(cellText)) {
                shouldDisplay = false;
            }
        });

        row.style.display = shouldDisplay ? '' : 'none';
    });
}

// ==========================
// Filter Dropdown 
// ==========================
function createDropdown(th, colIndex) {
    closeAllDropdowns(th);

    const existingDropdown = th.querySelector(".filter-dropdown");
    if (existingDropdown) {
        existingDropdown.classList.toggle("show");
        return;
    }

    th.classList.add("open");
    const dropdown = document.createElement("div");
    dropdown.className = "filter-dropdown";
    dropdown.addEventListener("click", e => e.stopPropagation()); // Prevent closing when clicking inside dropdown

    const thRect = th.getBoundingClientRect();
    dropdown.style.minWidth = thRect.width + "px";

    setTimeout(() => dropdown.classList.add("show"), 10);

    const tempValues = Array.from(document.querySelectorAll("table tbody tr")).map(row => {
        return row.cells[colIndex].textContent.toLowerCase();
    });

    const uniqueValues = Array.from(new Set(tempValues)).sort();

    // Select All checkbox
    const selectAllLabel = document.createElement("label");
    selectAllLabel.classList.add("select-all");
    const selectAllCheckbox = document.createElement("input");
    selectAllCheckbox.type = "checkbox";
    selectAllCheckbox.checked = uniqueValues.every(val => activeFilters[colIndex]?.includes(val));
    selectAllLabel.appendChild(selectAllCheckbox);
    selectAllLabel.appendChild(document.createTextNode(" Select All"));
    dropdown.appendChild(selectAllLabel);

    // Individual checkboxes
    uniqueValues.forEach(value => {
        const label = document.createElement("label");
        const checkbox = document.createElement("input");
        checkbox.type = "checkbox";
        checkbox.value = value;
        checkbox.checked = activeFilters[colIndex]?.includes(value);
        label.appendChild(checkbox);
        label.appendChild(document.createTextNode(" " + value));
        dropdown.appendChild(label);

        checkbox.addEventListener("change", () => {
            const checkboxes = Array.from(dropdown.querySelectorAll("input[type=checkbox]")).filter(cb => cb !== selectAllCheckbox);
            const checked = checkboxes.filter(cb => cb.checked).map(cb => cb.value);
            activeFilters[colIndex] = checked.length ? checked : null;
            if (!checked.length) delete activeFilters[colIndex];
            selectAllCheckbox.checked = checked.length === checkboxes.length;
            applyFilters(); 
        });
    });

    // Select All logic
    selectAllCheckbox.addEventListener("change", () => {
        const checkboxes = Array.from(dropdown.querySelectorAll("input[type=checkbox]")).filter(cb => cb !== selectAllCheckbox);
        checkboxes.forEach(cb => cb.checked = selectAllCheckbox.checked);
        if (selectAllCheckbox.checked) {
            activeFilters[colIndex] = uniqueValues;
        } else {
            delete activeFilters[colIndex];
        }
        applyFilters(); 
    });

    th.appendChild(dropdown);
}

// Close all dropdowns except the one clicked
function closeAllDropdowns(exceptTh = null) {
    document.querySelectorAll(".filter-dropdown.show").forEach(dropdown => {
        const parentTh = dropdown.closest("th");
        if (parentTh !== exceptTh) {
            dropdown.classList.remove("show");
            parentTh?.classList.remove("open");
            setTimeout(() => {
                if (dropdown.parentElement) dropdown.parentElement.removeChild(dropdown);
            }, 200);
        }
    });
}

// Add event listener for table header filter click
document.querySelectorAll('.filterable').forEach(th => {
    th.addEventListener('click', function (event) {
        event.stopPropagation(); 
        const colIndex = parseInt(th.dataset.column);
        createDropdown(th, colIndex);
    });
});

// Close filter dropdowns if clicked outside
document.addEventListener("click", (event) => {
    if (!event.target.closest(".filterable") && !event.target.closest(".filter-dropdown")) {
        closeAllDropdowns();
    }
});



// ==========================
// Appointment Chart Script
// ==========================
let appointmentChart = null;

function loadAppointmentChart() {
    console.log("Appointment Chart script loaded!");
    
    const statsEl = document.getElementById('stats-data');
    const canvas = document.getElementById('appointmentChart');
    const wrapper = document.querySelector('.chart-wrapper');

    // Check if necessary elements are present, and log warnings if not
    if (!statsEl || !canvas || !wrapper) {
        console.warn('Required elements for the appointment chart are missing.');
        return;
    }

    const stats = JSON.parse(statsEl.textContent);
    const ctx = canvas.getContext('2d');

    // Destroy existing chart if it exists to prevent duplicates
    if (appointmentChart) {
        appointmentChart.destroy();
    }

    // Initialize the chart
    appointmentChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Completed', 'Pending'],
            datasets: [{
                data: [stats.completed || 0, stats.pending || 0],
                backgroundColor: ['#28a745', '#ffc107'],
                borderColor: '#ffffff',
                borderWidth: 2,
                hoverOffset: 10,
                borderRadius: 5
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: {
                duration: 800,
                easing: 'easeOutQuart',
                onComplete: () => {
                    // Show chart wrapper after render
                    wrapper.classList.add('show');
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Appointments Status',
                    font: { size: 16, weight: 'bold' },
                    color: '#333'
                },
                legend: {
                    position: 'bottom',
                    labels: {
                        font: { size: 12, weight: 'bold' },
                        color: '#555',
                        padding: 20
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            const value = context.raw || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = total ? ((value / total) * 100).toFixed(1) : 0;
                            return `${context.label}: ${value} (${percentage}%)`;
                        }
                    }
                }
            }
        },
        plugins: getChartDataLabelsPlugin() 
    });
}

// Dynamically load ChartDataLabels plugin if available
function getChartDataLabelsPlugin() {
    return typeof ChartDataLabels !== 'undefined' ? [ChartDataLabels] : [];
}


// ==========================
// Modal Confirmation Script
// ==========================
function initModalConfirmations() {
    console.log("Modal script loaded!");

    // Flash messages auto-dismiss
    document.querySelectorAll(".alert-dismissible").forEach(msg => {
        setTimeout(() => {
            bootstrap.Alert.getOrCreateInstance(msg).close();
        }, 3000);
    });

    // Modal confirm buttons
    const confirmButtons = document.querySelectorAll('.confirm-btn');
    const modalEl = document.getElementById('confirmActionModal');
    const modal = new bootstrap.Modal(modalEl);
    const modalTitle = document.getElementById('confirmActionLabel');
    const modalBody = document.getElementById('confirmActionBody');
    const confirmActionBtn = document.getElementById('confirmActionBtn');

    // Cleanup backdrop if modal is hidden
    modalEl.addEventListener('hidden.bs.modal', () => {
        document.body.classList.remove('modal-open');
        document.querySelectorAll('.modal-backdrop').forEach(b => b.remove());
    });

    // Handle each action
    confirmButtons.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const url = this.getAttribute('href');
            const message = this.dataset.message || "Are you sure?";
            const action = this.dataset.action || "confirm";

            modalBody.textContent = message;
            confirmActionBtn.setAttribute('href', url);

            // Change modal title and button styles based on action
            if(action === "delete"){
                modalTitle.textContent = "Confirm Deletion";
                confirmActionBtn.className = "btn btn-danger";
                modalEl.querySelector('.modal-header').className = "modal-header bg-danger text-white";
            } else if(action === "cancel"){
                modalTitle.textContent = "Confirm Cancellation";
                confirmActionBtn.className = "btn btn-warning";
                modalEl.querySelector('.modal-header').className = "modal-header bg-warning text-dark";
            } else {
                modalTitle.textContent = "Confirm Action";
                confirmActionBtn.className = "btn btn-primary";
                modalEl.querySelector('.modal-header').className = "modal-header bg-primary text-white";
            }

            modal.show();
        });
    });
}




