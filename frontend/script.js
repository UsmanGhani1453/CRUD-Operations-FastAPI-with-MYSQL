console.log("SCRIPT IS CONNECTED AND RUNNING!");

document.addEventListener('DOMContentLoaded', () => {
    console.log("Step 1: HTML loaded. Looking for the form...");
    const loginForm = document.getElementById('loginForm');
    
    if (loginForm) {
        console.log("Step 2: Form found! Attaching submit listener.");
        
        loginForm.addEventListener('submit', async function (e) {
            e.preventDefault(); // Stop the page from refreshing
            console.log("Step 3: Login button clicked!");
            
            const usernameField = document.getElementById('username') || document.getElementById('email');
            const passwordField = document.getElementById('password');
            const errorMsg = document.getElementById('errorMsg');
            
            if (!usernameField || !passwordField) {
                console.error("ERROR: Could not find the input fields in the HTML!");
                return;
            }

            console.log("Step 4: Form data grabbed. Username:", usernameField.value);

            const formData = new URLSearchParams();
            formData.append('username', usernameField.value);
            formData.append('password', passwordField.value);

            try {
                console.log("Step 5: Sending request to FastAPI backend...");
                const response = await fetch('http://127.0.0.1:8000/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded'
                    },
                    body: formData
                });

                console.log("Step 6: Backend replied. Status code:", response.status);

                if (!response.ok) {
                    const errorText = await response.text();
                    console.error("Backend Error Details:", errorText);
                    throw new Error('Invalid email or password');
                }

                const data = await response.json();
                console.log("Step 7: Success! Token received, redirecting...");
                
                localStorage.setItem('access_token', data.access_token);
                window.location.href = 'dashboard.html';
                
            } catch (err) {
                console.error("Step 8: Code hit an error ->", err);
                if (errorMsg) {
                    errorMsg.textContent = err.message;
                }
            }
        });
    } else {
        console.error("CRITICAL ERROR: Could not find 'loginForm' in your index.html!");
    }
});