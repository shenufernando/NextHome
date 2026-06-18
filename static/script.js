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

// Pop-up එකෙන් පිටත ක්ලික් කරත් වැසෙන්න හැදීම
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
    // 1. Radio Button එක සිලෙක්ට් වෙලා තියෙනවද බලන්න
    let selectedRadio = document.querySelector('input[name="plan"]:checked');
    
    // වැරදීමකින්වත් සිලෙක්ට් වෙලා නැත්නම් function එක නතර කරන්න
    if (!selectedRadio) return; 
    
    let selectedPlan = selectedRadio.value;
    let premiumGalleryFields = document.querySelectorAll('.premium-gallery');
    let submitBtn = document.getElementById('submitBtn');
    
    console.log("Selected Plan Changed to:", selectedPlan); // බ්‍රවුසර් එකේ වැඩ කරනවද බලන්න (F12)

    if (selectedPlan === 'premium') {
        // Premium නම් පින්තූර 4, 5, 6 පෙන්වන්න
        premiumGalleryFields.forEach(field => {
            field.style.setProperty('display', 'block', 'important');
        });
        if (submitBtn) {
            submitBtn.innerHTML = "Request Approval (Rs. 3000)";
        }
    } else {
        // Basic නම් පින්තූර 4, 5, 6 හංගන්න
        premiumGalleryFields.forEach(field => {
            field.style.setProperty('display', 'none', 'important');
            
            // ඉන්පුට් එක ඇතුළේ ෆයිල් එකක් තිබ්බොත් Clear කරන්න
            let input = field.querySelector('input[type="file"]');
            if (input) input.value = "";
        });
        if (submitBtn) {
            submitBtn.innerHTML = "Request Approval (FREE)";
        }
    }
}

// පිටුව ලෝඩ් වෙද්දීම මේක එක පාරක් රන් කරන්න
document.addEventListener("DOMContentLoaded", function() {
    handlePackageChange();
});

// ==========================================
// 🛠️ 3. ADMIN PROPERTY ACTIONS & CONFIRMATIONS (FIXED)
// ==========================================

document.addEventListener("DOMContentLoaded", function() {
    // පිටුව ලෝඩ් වෙද්දී Add Property Form එකේ තත්ත්වය සකස් කිරීම
    if (document.getElementById('propertyType')) {
        toggleFields();
    }
    if (document.querySelector('input[name="plan"]')) {
        handlePackageChange();
    }
    
    // 🚦 1. Approve කිරීමට පෙර පැකේජ් එක අනුව තහවුරු කිරීමේ පණිවිඩය වෙනස් කිරීම
    const approveForms = document.querySelectorAll('.action-approve');
    approveForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            // ටේබල් රෝ එකෙන් මේක Basic ද Premium ද කියලා අඳුරගන්නවා (data attributes හෝ text හරහා)
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

    // 🛑 2. Reject කිරීමට පෙර තහවුරු කිරීම
    const rejectForms = document.querySelectorAll('.action-reject');
    rejectForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if(!confirm("Are you sure you want to REJECT this property listing?")) {
                e.preventDefault();
            }
        });
    });

    // ⚠️ 3. Delete කිරීමට පෙර තහවුරු කිරීම
    const deleteForms = document.querySelectorAll('.action-delete');
    deleteForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if(!confirm("⚠️ WARNING: Are you sure you want to PERMANENTLY DELETE this property from the database? This cannot be undone!")) {
                e.preventDefault();
            }
        });
    });
});