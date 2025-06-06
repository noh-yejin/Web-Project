
document.addEventListener('DOMContentLoaded', async function () {
    const userId = sessionStorage.getItem("user_id");

    if (!userId) {
    alert("User not logged in.");
    window.location.href = "/static/html/login.html";
    return;
    }

    try {
    const response = await fetch(`/users/${userId}`);
    const data = await response.json();

    if (response.ok) {
        document.getElementById("user-id").textContent = data.user_id || "-";
        document.getElementById("user-email").textContent = data.email || "-";
        document.getElementById("signup-date").textContent = data.signup_date || "-";
    } else {
        alert("Failed to load user information.");
    }
    } catch (error) {
    console.error("Error fetching user info:", error);
    alert("Error loading account information.");
    }

    // ❌ 계정 삭제 버튼
    document.querySelector(".delete-btn").addEventListener("click", async () => {
    if (!confirm("Are you sure you want to delete your account? This action cannot be undone.")) return;

    try {
        const deleteResponse = await fetch(`/users/${userId}`, {
        method: "DELETE"
        });

        if (deleteResponse.ok) {
        alert("Account deleted successfully.");
        sessionStorage.clear();
        window.location.href = "/static/html/login.html";
        } else {
        alert("Failed to delete account.");
        }
    } catch (error) {
        console.error("Delete error:", error);
        alert("An error occurred while deleting your account.");
    }
    });
});
