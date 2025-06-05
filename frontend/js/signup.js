document.addEventListener('DOMContentLoaded', function () {
  const emailDomainSelect = document.getElementById('signup-email-domain');
  const emailFinalInput = document.getElementById('signup-email-final');
  const emailDomainCustom = document.createElement('input');
  emailDomainCustom.type = 'text';
  emailDomainCustom.id = 'signup-email-domain-custom';
  emailDomainCustom.placeholder = 'Custom input';
  emailDomainCustom.style.flex = '1';
  emailDomainCustom.style.padding = '10px';
  emailDomainCustom.style.marginTop = '8px';
  emailDomainCustom.style.marginBottom = '8px';
  emailDomainCustom.style.border = '1px solid #ccc';
  emailDomainCustom.style.borderRadius = '4px';
  emailDomainCustom.style.boxSizing = 'border-box';

  let isCustomDomain = false;

  // 이메일 도메인 선택 시 커스텀 입력창으로 교체
  emailDomainSelect.addEventListener('change', function () {
    if (this.value === 'self' && !isCustomDomain) {
      this.replaceWith(emailDomainCustom);
      isCustomDomain = true;
    }
  });

  // ✅ ID 중복 체크 (API 호출 기반)
  document.getElementById('signup-id').addEventListener('input', async function () {
    const inputId = this.value.trim();
    const resultDiv = document.getElementById('id-check-result');

    if (!inputId) {
      resultDiv.textContent = '';
      return;
    }

    try {
      const response = await fetch(`http://localhost:8000/check_id?user_id=${encodeURIComponent(inputId)}`);
      const result = await response.json();

      if (response.ok) {
        if (result.exists) {
          resultDiv.textContent = 'This username is already taken.';
          resultDiv.style.color = 'red';
        } else {
          resultDiv.textContent = 'This username is available.';
          resultDiv.style.color = 'green';
        }
      } else {
        resultDiv.textContent = 'Error checking ID.';
        resultDiv.style.color = 'orange';
      }
    } catch (error) {
      console.error('ID check error:', error);
      resultDiv.textContent = 'Error checking ID.';
      resultDiv.style.color = 'orange';
    }
  });

  // 비밀번호 일치 확인용 요소 추가
  const pwInput = document.getElementById('signup-pw');
  const pwConfirmInput = document.getElementById('signup-pw-confirm');
  const pwCheckResult = document.createElement('div');
  pwCheckResult.style.fontSize = '12px';
  pwCheckResult.style.marginBottom = '8px';
  pwConfirmInput.insertAdjacentElement('afterend', pwCheckResult);

  function checkPasswordMatch() {
    const pw = pwInput.value.trim();
    const pwConfirm = pwConfirmInput.value.trim();

    if (!pw || !pwConfirm) {
      pwCheckResult.textContent = '';
      return;
    }

    if (pw === pwConfirm) {
      pwCheckResult.textContent = 'Passwords match.';
      pwCheckResult.style.color = 'green';
    } else {
      pwCheckResult.textContent = 'Passwords do not match.';
      pwCheckResult.style.color = 'red';
    }
  }
  function togglePassword(id, button) {
    const input = document.getElementById(id);
    const isVisible = input.type === 'text';
    input.type = isVisible ? 'password' : 'text';
    button.textContent = isVisible ? '🙉' : '🙈';
  }

  pwInput.addEventListener('input', checkPasswordMatch);
  pwConfirmInput.addEventListener('input', checkPasswordMatch);

  // 회원가입 버튼 클릭 시 처리
  document.getElementById('signup-btn').addEventListener('click', async function () {
    const id = document.getElementById('signup-id').value.trim();
    const pw = pwInput.value.trim();
    const pwConfirm = pwConfirmInput.value.trim();
    const gender = document.getElementById('signup-gender').value.trim();
    const emailId = document.getElementById('signup-email-id').value.trim();

    let emailDomain = isCustomDomain
      ? emailDomainCustom.value.trim()
      : emailDomainSelect.value;

    const marketing = document.getElementById('signup-marketing').checked;

    // 비밀번호 일치 확인
    if (pw !== pwConfirm) {
      alert('Passwords do not match.');
      return;
    }

    // 이메일 완성
    const fullEmail = emailId + '@' + emailDomain;
    emailFinalInput.value = fullEmail;

    // 회원가입 API 호출
    try {
      const response = await fetch('http://localhost:8000/signup', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
        user_id: id,
        password: pw,
        password_confirm: pwConfirm,  // 👈 누락된 필드 추가!
        gender,
        email: fullEmail,
        marketing
        })
      });

      const result = await response.json();

      if (response.ok) {
        alert('Signup completed successfully!');
        location.href = '/static/html/login.html';
      } else {
        alert('Signup failed: ' + result.message);
      }
    } catch (error) {
      console.error('Signup error:', error);
      alert('An unexpected error occurred. Please try again later.');
    }
  });
});

