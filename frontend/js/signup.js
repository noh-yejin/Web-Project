document.addEventListener('DOMContentLoaded', function () {
  const emailDomainSelect = document.getElementById('signup-email-domain');
  const emailFinalInput = document.getElementById('signup-email-final');
  const emailDomainCustom = document.createElement('input');
  const now = new Date();
  const signupDate = now.toISOString().split('T')[0];

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

  emailDomainSelect.addEventListener('change', function () {
    if (this.value === 'self' && !isCustomDomain) {
      this.replaceWith(emailDomainCustom);
      isCustomDomain = true;
    }
  });

  document.getElementById('signup-id').addEventListener('input', async function () {
    const inputId = this.value.trim();
    const resultDiv = document.getElementById('id-check-result');

    if (!inputId) {
      resultDiv.textContent = '';
      return;
    }

    try {
      const response = await fetch(`/check_id?user_id=${encodeURIComponent(inputId)}`);
      const result = await response.json();

      if (response.ok) {
        resultDiv.textContent = result.exists
          ? 'This username is already taken.'
          : 'This username is available.';
        resultDiv.style.color = result.exists ? 'red' : 'green';
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

  // ✅ 바로 연결
  const pwBtn = document.getElementById('pw-toggle-btn');
  const pwConfirmBtn = document.getElementById('pw-confirm-toggle-btn');

  if (pwBtn) {
    pwBtn.addEventListener('click', function () {
      togglePassword('signup-pw', this);
    });
  }

  if (pwConfirmBtn) {
    pwConfirmBtn.addEventListener('click', function () {
      togglePassword('signup-pw-confirm', this);
    });
  }

  pwInput.addEventListener('input', checkPasswordMatch);
  pwConfirmInput.addEventListener('input', checkPasswordMatch);

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

    if (pw !== pwConfirm) {
      alert('Passwords do not match.');
      return;
    }

    const fullEmail = `${emailId}@${emailDomain}`;
    emailFinalInput.value = fullEmail;

    try {
      const response = await fetch('/signup', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          user_id: id,
          password: pw,
          password_confirm: pwConfirm,
          gender,
          email: fullEmail,
          marketing,
          signup_date: signupDate
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
