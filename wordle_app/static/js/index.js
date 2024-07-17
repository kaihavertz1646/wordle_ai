document.querySelectorAll('.form input, .form textarea').forEach(element => {
    element.addEventListener('keyup', event => handleInputEvent(event));
    element.addEventListener('blur', event => handleInputEvent(event));
    element.addEventListener('focus', event => handleInputEvent(event));
  });
  
  function handleInputEvent(e) {
    var $this = e.target,
        label = $this.previousElementSibling;
  
    if (e.type === 'keyup') {
      if ($this.value === '') {
        label.classList.remove('active', 'highlight');
      } else {
        label.classList.add('active', 'highlight');
      }
    } else if (e.type === 'blur') {
      if ($this.value === '') {
        label.classList.remove('active', 'highlight');
      } else {
        label.classList.remove('highlight');
      }
    } else if (e.type === 'focus') {
      if ($this.value === '') {
        label.classList.remove('highlight');
      } else if ($this.value !== '') {
        label.classList.add('highlight');
      }
    }
  }
  
  document.querySelectorAll('.tab a').forEach(tab => {
    tab.addEventListener('click', event => {
      event.preventDefault();
      tab.parentElement.classList.add('active');
      Array.from(tab.parentElement.parentElement.children).forEach(sibling => {
        if (sibling !== tab.parentElement) {
          sibling.classList.remove('active');
        }
      });
  
      const target = document.querySelector(tab.getAttribute('href'));
      Array.from(target.parentElement.children).forEach(content => {
        content.style.display = 'none';
      });
      target.style.display = 'block';
    });
  });
  

  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

document.querySelectorAll('.form input, .form textarea').forEach(element => {
  element.addEventListener('keyup', event => handleInputEvent(event));
  element.addEventListener('blur', event => handleInputEvent(event));
  element.addEventListener('focus', event => handleInputEvent(event));
});

function handleInputEvent(e) {
  var $this = e.target,
      label = $this.previousElementSibling;

  if (e.type === 'keyup') {
      if ($this.value === '') {
          label.classList.remove('active', 'highlight');
      } else {
          label.classList.add('active', 'highlight');
      }
  } else if (e.type === 'blur') {
      if ($this.value === '') {
          label.classList.remove('active', 'highlight');
      } else {
          label.classList.remove('highlight');
      }
  } else if (e.type === 'focus') {
      if ($this.value !== '') {
          label.classList.add('highlight');
      }
  }
}

document.querySelectorAll('.tab a').forEach(tab => {
  tab.addEventListener('click', function(e) {
      e.preventDefault();
      const parent = this.parentElement;
      parent.classList.add('active');
      parent.siblings.forEach(sibling => sibling.classList.remove('active'));

      const target = document.querySelector(this.getAttribute('href'));
      document.querySelectorAll('.tab-content > div').forEach(div => div.style.display = 'none');
      target.style.display = 'block';
  });
});