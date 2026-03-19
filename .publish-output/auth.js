// Client-side password gate — SHA-256 hash comparison
// Note: this is a convenience gate, not military-grade security.
// The hash is visible in source, but adequate for keeping casual visitors out.

var EXPECTED_HASH = '5a20fe2f1b70d1150712b032c84f5998ac797d1bd9c84ed2ada77866ea030287';

async function sha256(message) {
  var encoder = new TextEncoder();
  var data = encoder.encode(message);
  var hash = await crypto.subtle.digest('SHA-256', data);
  var hashArray = Array.from(new Uint8Array(hash));
  return hashArray.map(function(b) { return b.toString(16).padStart(2, '0'); }).join('');
}

function showSite() {
  var wall = document.getElementById('auth-wall');
  var content = document.getElementById('site-content');
  if (wall) wall.style.display = 'none';
  if (content) content.style.display = 'block';
}

async function checkAuth() {
  var input = document.getElementById('auth-password');
  var error = document.getElementById('auth-error');
  if (!input) return;

  var hash = await sha256(input.value);
  if (hash === EXPECTED_HASH) {
    sessionStorage.setItem('publish-auth', 'ok');
    showSite();
  } else {
    if (error) error.style.display = 'block';
    input.value = '';
    input.focus();
  }
}

document.addEventListener('DOMContentLoaded', function() {
  var wall = document.getElementById('auth-wall');
  var content = document.getElementById('site-content');

  if (sessionStorage.getItem('publish-auth') === 'ok') {
    showSite();
    return;
  }

  if (wall) wall.style.display = 'block';
  if (content) content.style.display = 'none';

  var input = document.getElementById('auth-password');
  if (input) {
    input.addEventListener('keydown', function(e) {
      if (e.key === 'Enter') checkAuth();
    });
  }
});
