function askQuestion() {
    const userInput = document.getElementById("user-input").value;
    if (!userInput.trim()) return;

    const chatBox = document.getElementById("chat-box");
    const sendButton = document.getElementById("send-button");
    const loader = document.getElementById("loader");
    const inputField = document.getElementById("user-input");
    const overlay = document.getElementById('overlay');

    const userMessage = document.createElement("div");
    userMessage.classList.add("message", "user-message");
    userMessage.textContent = `${userInput}`;
    chatBox.appendChild(userMessage);

    sendButton.disabled = true;
    inputField.disabled = true;
    overlay.classList.add('show');
    loader.style.display = "inline-block";

    chatBox.scrollTop = chatBox.scrollHeight;

    inputField.value = "";

    fetch('/ask', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `query=${userInput}`,
    })
    .then(response => response.json())
    .then(data => {
        loader.style.display = "none";
        sendButton.disabled = false;
        inputField.disabled = false;
        overlay.classList.remove('show');

        const aiMessage = document.createElement("div");
        aiMessage.classList.add("message", "ai-message");
        aiMessage.textContent = `${data.answer}`;
        chatBox.appendChild(aiMessage);

        chatBox.scrollTop = chatBox.scrollHeight;
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error:', error);
        loader.style.display = "none";
        sendButton.disabled = false;
        inputField.disabled = false;
        overlay.classList.remove('show');
    });
}
