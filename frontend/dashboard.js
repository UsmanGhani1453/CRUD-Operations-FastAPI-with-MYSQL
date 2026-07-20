document.addEventListener('DOMContentLoaded', async function () {
    const token = localStorage.getItem('access_token');
    const dataArea = document.getElementById('dataArea');
    
    if (!token) {
        window.location.href = 'index.html';
        return;
    }

    try {
        console.log("Token found! Attempting to fetch user data...");
        
        const response = await fetch('http://127.0.0.1:8000/users/me', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            const errorDetails = await response.text();
            console.error("Backend Error Details:", errorDetails);
            throw new Error('Failed to fetch user data');
        }

        const userData = await response.json();
        console.log("Data received:", userData);
        
        // Format the verification status for a better user experience
        let verificationStatus = "Unverified ❌ (Please check your email)";
        let statusColor = "#d9534f"; // Red
        
        if (userData.is_verified === true) {
            verificationStatus = "Verified ✅";
            statusColor = "#5cb85c"; // Green
        }

        // Inject structured HTML into the data area instead of raw JSON
        dataArea.innerHTML = `
            <div style="margin-top: 15px; padding: 15px; border: 1px solid #ccc; border-radius: 5px; background-color: #f9f9f9;">
                <h3 style="margin-top: 0;">Account Details</h3>
                <p style="margin-bottom: 8px;"><strong>ID:</strong> ${userData.id}</p>
                <p style="margin-bottom: 8px;"><strong>Email:</strong> ${userData.email}</p>
                <p style="margin-bottom: 0;"><strong>Status:</strong> <span style="color: ${statusColor}; font-weight: bold;">${verificationStatus}</span></p>
            </div>
        `;
        
    } catch (err) {
        console.error("Dashboard script caught an error:", err);
        
        // Update the UI so the user knows something went wrong, replacing the "Loading..." text
        dataArea.innerHTML = `
            <p style="color: #d9534f; font-weight: bold;">
                Failed to load profile data. Please check your console for details.
            </p>
        `;
        
        // REDIRECT DISABLED FOR DEBUGGING:
        // localStorage.removeItem('access_token');
        // window.location.href = 'index.html'; 
    }

    // Logout handler
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function () {
            localStorage.removeItem('access_token');
            window.location.href = 'index.html';
        });
    }
});