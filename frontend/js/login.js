// 로그인 버튼 클릭 이벤트 처리
// Login button click event handler

document.getElementById('login-btn').addEventListener('click', async function () {
  // 입력된 사용자 ID와 비밀번호를 가져옴
  // Get entered user ID and password
  const loginId = document.getElementById('login-id').value.trim();
  const loginPw = document.getElementById('login-pw').value.trim();

  try {
    // 로그인 요청 전송
    // Send login request to server
    const response = await fetch('http://localhost:8000/login', {
      method: 'POST', // POST 방식 사용 / Use POST method
      headers: {
        'Content-Type': 'application/json' // JSON 형식 명시 / Specify JSON format
      },
      body: JSON.stringify({
        user_id: loginId,  // 사용자 ID / User ID
        password: loginPw  // 비밀번호 / Password
      })
    });

    const result = await response.json(); // 응답 데이터 파싱 / Parse response data

    if (response.ok) {
      // 로그인 성공 시 세션에 사용자 ID 저장 후 메인 페이지로 이동
      // On success, store user ID in session and redirect
      sessionStorage.setItem('user_id', result.user_id);
      location.href = "/static/html/main.html";
    } else {
      // 로그인 실패 시 알림 표시
      // Show alert if login failed
      Swal.fire({
        icon: 'error',
        title: 'Login Failed', // 로그인 실패 / Login failed
        text: 'Incorrect user ID or password.', // 아이디 또는 비밀번호 오류 / Wrong credentials
        confirmButtonColor: '#3085d6',
        confirmButtonText: 'OK',
        allowOutsideClick: true,
        allowEscapeKey: true,
        allowEnterKey: true,
        backdrop: true,
        scrollbarPadding: false
      });
    }
  } catch (error) {
    // 네트워크 또는 서버 오류 처리
    // Handle network or server error
    console.error('Login error:', error);
    Swal.fire({
      icon: 'error',
      title: 'Error Occurred', // 오류 발생 / Error occurred
      text: 'A server error occurred. Please try again later.', // 서버 오류 메시지 / Server error message
      confirmButtonText: 'Close'
    });
  }
});