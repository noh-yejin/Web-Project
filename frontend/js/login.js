document.getElementById('login-btn').addEventListener('click', function () {
  const loginId = document.getElementById('login-id').value.trim();
  const loginPw = document.getElementById('login-pw').value.trim();

  const users = JSON.parse(localStorage.getItem('user_info')) || [];

  const matchedUser = users.find(user => user.id === loginId && user.password === loginPw);

  if (matchedUser) {
    alert('로그인 성공!');
    // 여기에 로그인 후 이동할 페이지 추가
    location.href = "../html/team_project.html";
  } else {
    alert('아이디 또는 비밀번호가 일치하지 않습니다.');
  }
});
