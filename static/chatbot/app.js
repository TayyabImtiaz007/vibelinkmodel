class Chatbox {
  constructor() {
    this.args = {
      openButton: document.querySelector('.chatbox__button'),
      chatBox: document.querySelector('.chatbox__support'),
      sendButton: document.querySelector('.send__button'),
      textField: document.querySelector('.chatbox__support input[name="user_input"]'), // Reference text field directly
    };
    this.state = false;
    this.messages = [];
  }

  display() {
    this.args.openButton.addEventListener('click', () => this.toggleState());
    this.args.sendButton.addEventListener('click', (event) => {
      event.preventDefault(); // Prevent form submission
      this.onSendButton();
    });
    this.args.textField.addEventListener("keyup", ({ key }) => { 
      if (key === "Enter") this.onSendButton();
    });
  }

  toggleState() {
    this.state = !this.state;
    this.args.chatBox.classList.toggle('chatbox--active', this.state);
  }

  onSendButton() {
    const text = this.args.textField.value.trim(); 
    if (text === "") return;

    this.messages.push({ name: "User", message: text });
    this.updateChatText();
    this.args.textField.value = ''; 

    const csrftoken = this.getCookie('csrftoken'); // Get CSRF token

    console.log('Sending message:', text);

    fetch('/chatbot/predict/', {  // Updated URL path
      method: 'POST',
      body: JSON.stringify({ message: text }),
      mode: 'cors',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrftoken // Include CSRF token
      },
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json();
    })
    .then(data => {
      console.log('Response received:', data);
      const isSlotsMessage = data.response.includes('Slot');
      if (isSlotsMessage) {
        this.displaySlots(data.response);
      } else {
        this.messages.push({ name: "Sam", message: data.response });
        this.updateChatText();
      }
    })
    .catch(error => {
      console.error('Error:', error);
      this.updateChatText();
    }); 
  }

  updateChatText() {
    const chatMessage = this.args.chatBox.querySelector('.chatbox__messages');
    chatMessage.innerHTML = this.messages.slice().reverse().map(item => `
      <div class="messages__item messages__item--${item.name.toLowerCase()}">${item.message}</div>
    `).join('');
    chatMessage.scrollTop = chatMessage.scrollHeight; 
  }

  displaySlots(slotsMessage) {
    const slots = slotsMessage.split('\n');
    slots.forEach(slot => {
      this.messages.push({ name: "Sam", message: slot });
    });
    this.updateChatText();
  }

  getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
}

const chatbox = new Chatbox();
chatbox.display();
