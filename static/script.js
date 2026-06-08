// 1. Search Filter Function
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

// 2. Open Modal and Fill Data
function openEditModal(id, name, email, role) {
    // Form එක submit විය යුතු නිවැරදි URL එක dynamically සැකසීම
    document.getElementById('editForm').action = "/edit_user/" + id;
    
    // Pop-up එක ඇතුළේ ඇති Input වලට පරණ දත්ත ටික දැමීම
    document.getElementById('modal_name').value = name;
    document.getElementById('modal_email').value = email;
    document.getElementById('modal_role').value = role;
    
    // Pop-up එක පෙන්වීම
    document.getElementById('editModal').style.display = 'flex';
}

// 3. Close Modal
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


//add property
function toggleFields() {
    let propertyType = document.getElementById('propertyType').value;
    let residentialFields = document.querySelectorAll('.residential-fields');
    
    if (propertyType === 'land') {
        residentialFields.forEach(field => field.style.display = 'none');
    } else {
        residentialFields.forEach(field => field.style.display = 'flex');
    }
}

function handlePackageChange() {
    let selectedPlan = document.querySelector('input[name="plan"]:checked').value;
    let premiumGalleryFields = document.querySelectorAll('.premium-gallery');
    let submitBtn = document.getElementById('submitBtn');
    
    if (selectedPlan === 'premium') {
        // Premium නම් පින්තූර 6ම පෙන්වනවා
        premiumGalleryFields.forEach(field => field.style.display = 'flex');
        submitBtn.innerHTML = "Request Approval (Rs. 3000)";
    } else {
        // Basic නම් පින්තූර 3යි
        premiumGalleryFields.forEach(field => field.style.display = 'none');
        submitBtn.innerHTML = "Request Approval (FREE)";
    }
}

// පිටුව මුලින්ම ලෝඩ් වෙද්දී ක්‍රියාත්මක වීම
document.addEventListener("DOMContentLoaded", function() {
    toggleFields();
    handlePackageChange();
});