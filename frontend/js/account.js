// 사용자 계정 정보를 불러오고, 계정 삭제 기능을 처리합니다.
// Loads user account information and handles account deletion.

document.addEventListener('DOMContentLoaded', async function () {
    const userId = sessionStorage.getItem("user_id"); // 세션에서 사용자 ID 가져오기 / Get user ID from session

    if (!userId) {
        alert("User not logged in."); // 로그인하지 않은 경우 알림 / Alert if not logged in
        window.location.href = "/static/html/login.html"; // 로그인 페이지로 이동 / Redirect to login
        return;
    }

    try {
        const response = await fetch(`/users/${userId}`); // 사용자 정보 요청 / Fetch user info
        const data = await response.json(); // 응답 데이터를 JSON으로 파싱 / Parse response

        if (response.ok) {
            // 사용자 정보를 화면에 표시 / Display user info
            document.getElementById("user-id").textContent = data.user_id || "-";
            document.getElementById("user-email").textContent = data.email || "-";
            document.getElementById("signup-date").textContent = data.signup_date || "-";
        } else {
            alert("Failed to load user information."); // 정보 로딩 실패 시 알림 / Alert if loading fails
        }
    } catch (error) {
        console.error("Error fetching user info:", error); // 오류 콘솔 출력 / Log error
        alert("Error loading account information."); // 오류 알림 / Alert error
    }

    // 계정 삭제 버튼 이벤트 리스너 / Delete button event listener
    document.querySelector(".delete-btn").addEventListener("click", async () => {
        if (!confirm("Are you sure you want to delete your account? This action cannot be undone.")) return;
        // 계정 삭제 확인 / Confirm deletion

        try {
            const deleteResponse = await fetch(`/users/${userId}`, {
                method: "DELETE" // DELETE 요청 / HTTP DELETE request
            });

            if (deleteResponse.ok) {
                alert("Account deleted successfully."); // 성공 알림 / Success alert
                sessionStorage.clear(); // 세션 초기화 / Clear session
                window.location.href = "/static/html/login.html"; // 로그인 페이지로 이동 / Redirect to login
            } else {
                alert("Failed to delete account."); // 실패 알림 / Failure alert
            }
        } catch (error) {
            console.error("Delete error:", error); // 삭제 오류 콘솔 출력 / Log delete error
            alert("An error occurred while deleting your account."); // 삭제 중 오류 알림 / Alert error
        }
    });
});
