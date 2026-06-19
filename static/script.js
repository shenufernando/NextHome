// ==========================================
// 👤 1. ADMIN USER MANAGEMENT FUNCTIONS
// ==========================================

// Search Filter Function
function filterUsers() {
    let input = document.getElementById('userSearch').value.toLowerCase();
    let rows = document.getElementById('userTable').getElementsByTagName('tr');
    
    for (let i = 0; i < rows.length; i++) {
        let name = rows[i].querySelector('.username');
        let email = rows[i].querySelector('.useremail');
        if (name || email) {
            let textValue = (name.textContent + email.textContent).toLowerCase();
            rows[i].style.display = textValue.includes(input) ? "" : "none";
        }
    }
}

// Open Modal and Fill Data
function openEditModal(id, name, email, role) {
    document.getElementById('editForm').action = "/edit_user/" + id;
    document.getElementById('modal_name').value = name;
    document.getElementById('modal_email').value = email;
    document.getElementById('modal_role').value = role;
    document.getElementById('editModal').style.display = 'flex';
}

// Close Modal
function closeEditModal() {
    document.getElementById('editModal').style.display = 'none';
}

// Pop-up 
window.onclick = function(event) {
    let modal = document.getElementById('editModal');
    if (event.target == modal) {
        modal.style.display = "none";
    }
}


// ==========================================
// 🏢 2. ADD PROPERTY FORM FUNCTIONS (FIXED)
// ==========================================

function handlePackageChange() {
    // 1. Radio Button 
    let selectedRadio = document.querySelector('input[name="plan"]:checked');
    
    if (!selectedRadio) return; 
    
    let selectedPlan = selectedRadio.value;
    let premiumGalleryFields = document.querySelectorAll('.premium-gallery');
    let submitBtn = document.getElementById('submitBtn');
    
    console.log("Selected Plan Changed to:", selectedPlan); 

    if (selectedPlan === 'premium') {
        // Premium image 4, 5, 6 
        premiumGalleryFields.forEach(field => {
            field.style.setProperty('display', 'block', 'important');
        });
        if (submitBtn) {
            submitBtn.innerHTML = "Request Approval (Rs. 3000)";
        }
    } else {
        // Basic  4, 5, 6 hide
        premiumGalleryFields.forEach(field => {
            field.style.setProperty('display', 'none', 'important');
            
           
            let input = field.querySelector('input[type="file"]');
            if (input) input.value = "";
        });
        if (submitBtn) {
            submitBtn.innerHTML = "Request Approval (FREE)";
        }
    }
}

document.addEventListener("DOMContentLoaded", function() {
    handlePackageChange();
});

// ==========================================
// 🛠️ 3. ADMIN PROPERTY ACTIONS & CONFIRMATIONS (FIXED)
// ==========================================

document.addEventListener("DOMContentLoaded", function() {
    // Add Property Form 
    if (document.getElementById('propertyType')) {
        toggleFields();
    }
    if (document.querySelector('input[name="plan"]')) {
        handlePackageChange();
    }
    
    // 🚦 1. Approve 
    const approveForms = document.querySelectorAll('.action-approve');
    approveForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            //  Basic , Premium  (data attributes , text )
            let isPremium = form.closest('tr').textContent.toLowerCase().includes('premium');
            
            let message = "Are you sure you want to APPROVE this Basic property listing? It will go live immediately.";
            if (isPremium) {
                message = "Are you sure you want to APPROVE this Premium property listing? It will be sent to the seller for Rs. 3,000.00 payment before going live.";
            }
            
            if(!confirm(message)) {
                e.preventDefault(); 
            }
        });
    });

    // 🛑 2. Reject
    const rejectForms = document.querySelectorAll('.action-reject');
    rejectForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if(!confirm("Are you sure you want to REJECT this property listing?")) {
                e.preventDefault();
            }
        });
    });

    // ⚠️ 3. Delete 
    const deleteForms = document.querySelectorAll('.action-delete');
    deleteForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if(!confirm("⚠️ WARNING: Are you sure you want to PERMANENTLY DELETE this property from the database? This cannot be undone!")) {
                e.preventDefault();
            }
        });
    });
});