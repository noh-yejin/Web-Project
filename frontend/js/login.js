document.getElementById('login-btn').addEventListener('click', async function () {
  const loginId = document.getElementById('login-id').value.trim();
  const loginPw = document.getElementById('login-pw').value.trim();

  try {
    const response = await fetch('http://localhost:8000/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        user_id: loginId,
        password: loginPw
      })
    });

    const result = await response.json();

    if (response.ok) {
      sessionStorage.setItem('user_id', result.user_id);
      location.href = "/static/html/main.html";
    } else {
      Swal.fire({
        icon: 'error',
        title: 'Login Failed',
        text: 'Incorrect user ID or password.',
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
    console.error('Login error:', error);
    Swal.fire({
      icon: 'error',
      title: 'Error Occurred',
      text: 'A server error occurred. Please try again later.',
      confirmButtonText: 'Close'
    });
  }
});
