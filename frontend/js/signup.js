document.addEventListener('DOMContentLoaded', function () {
  const emailDomainSelect = document.getElementById('signup-email-domain');
  const emailFinalInput = document.getElementById('signup-email-final');
  const emailDomainCustom = document.createElement('input');
  emailDomainCustom.type = 'text';
  emailDomainCustom.id = 'signup-email-domain';
  emailDomainCustom.placeholder = 'Custom input';
  emailDomainCustom.style.flex = '1';
  emailDomainCustom.style.padding = '10px';
  emailDomainCustom.style.marginTop = '8px';
  emailDomainCustom.style.marginBottom = '8px';
  emailDomainCustom.style.border = '1px solid #ccc';
  emailDomainCustom.style.borderRadius = '4px';
  emailDomainCustom.style.boxSizing = 'border-box';

  let isCustomDomain = false;

  // When email domain selection changes
  emailDomainSelect.addEventListener('change', function () {
    if (this.value === 'self' && !isCustomDomain) {
      this.replaceWith(emailDomainCustom);
      isCustomDomain = true;
    }
  });

  // Check duplicate ID
  document.getElementById('signup-id').addEventListener('input', function () {
    const inputId = this.value.trim();
    const users = JSON.parse(localStorage.getItem('user_info')) || [];

    const isDuplicate = users.some(user => user.id === inputId);
    const resultDiv = document.getElementById('id-check-result');

    if (isDuplicate) {
      resultDiv.textContent = 'This username is already taken.';
      resultDiv.style.color = 'red';
    } else {
      resultDiv.textContent = 'This username is available.';
      resultDiv.style.color = 'green';
    }
  });

  // Real-time password match check
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

  pwInput.addEventListener('input', checkPasswordMatch);
  pwConfirmInput.addEventListener('input', checkPasswordMatch);

  // When signup button is clicked
  document.getElementById('signup-btn').addEventListener('click', function () {
    const id = document.getElementById('signup-id').value.trim();
    const pw = pwInput.value.trim();
    const pwConfirm = pwConfirmInput.value.trim();
    const gender = document.getElementById('signup-gender').value.trim();
    const emailId = document.getElementById('signup-email-id').value.trim();

    let emailDomain = isCustomDomain
      ? emailDomainCustom.value.trim()
      : emailDomainSelect.value;

    const marketing = document.getElementById('signup-marketing').checked;

    const users = JSON.parse(localStorage.getItem('user_info')) || [];

    // Check duplicate ID
    const isDuplicate = users.some(user => user.id === id);
    if (isDuplicate) {
      alert('User information already exists!');
      return;
    }

    // Confirm passwords match
    if (pw !== pwConfirm) {
      alert('Passwords do not match.');
      return;
    }

    // Save final email
    const fullEmail = emailId + '@' + emailDomain;
    emailFinalInput.value = fullEmail;

    // Save user info
    const newUser = {
      id,
      password: pw,
      gender,
      email: fullEmail,
      marketing
    };

    users.push(newUser);
    localStorage.setItem('user_info', JSON.stringify(users));

    alert('Signup completed successfully!');
    location.href = '../html/login.html';
  });
});
