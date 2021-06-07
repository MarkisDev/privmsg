
// Function to encrypt text
function encryptText(text, password)
{
	password = "hi";
	return CryptoJS.AES.encrypt(text, password).toString();
}

// Function to decrypt text
function decryptText(ciphertext, password)
{
    password = "hi";
    const bytes = CryptoJS.AES.decrypt(ciphertext, password);
    const originalText = bytes.toString(CryptoJS.enc.Utf8);
    return originalText;
}

// Called when room.html body loads
function initWS()
{
	const roomName = JSON.parse(document.getElementById('room-name').textContent);
	// Initialize WebSocket
	const chatSocket = new WebSocket(
		'ws://'
		+ window.location.host
		+ '/ws/chat/'
		+ roomName
		+ '/'
	);
	// Function that runs on message send
	chatSocket.onmessage = function (e)
	{
		const username = JSON.parse(document.getElementById('username').textContent);
		const password = getCookie('password');
		const data = JSON.parse(e.data);
		console.log(data.username);
		document.querySelector('#chat-log').value += (decryptText(data.username, password)) + ":" + (decryptText(data.message, password) + '\n');
	};
	// If WebSocket closes
	chatSocket.onclose = function (e)
	{
		console.error('Chat socket closed unexpectedly');
	};

	document.querySelector('#chat-message-input').focus();
	document.querySelector('#chat-message-input').onkeyup = function (e)
	{
		// If message not empty and enter, return is pressed
		if (this.value.trim() != '' && e.keyCode === 13)
		{  // enter, return
			document.querySelector('#chat-message-submit').click();
		}
	};
	// TO get cookies
	function getCookie(cname)
	{
		var name = cname + "=";
		var decodedCookie = decodeURIComponent(document.cookie);
		var ca = decodedCookie.split(';');
		for (var i = 0; i < ca.length; i++)
		{
			var c = ca[i];
			while (c.charAt(0) == ' ')
			{
				c = c.substring(1);
			}
			if (c.indexOf(name) == 0)
			{
				return c.substring(name.length, c.length);
			}
		}
		return "";
	}
	document.querySelector('#chat-message-submit').onclick = function (e)
	{
		const username = JSON.parse(document.getElementById('username').textContent);
		const password = getCookie('password');
		const messageInputDom = document.querySelector('#chat-message-input');
		const message = messageInputDom.value;
		// If message not empty
		if(message.trim() != '')
		{
			chatSocket.send(JSON.stringify({
				'message': encryptText(message, password),
				'username': encryptText(username, password)
			}));
			messageInputDom.value = '';
		}
	};
}

function setCookie()
{
	const password = document.querySelector('#password').value;
	document.cookie = "password=" + password;
}