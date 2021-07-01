
// Function to encrypt text
function encryptText(text, password)
{
    return CryptoJS.AES.encrypt(text, password).toString();
}

// Function to decrypt text
function decryptText(ciphertext, password)
{
    const bytes = CryptoJS.AES.decrypt(ciphertext, password);
    const originalText = bytes.toString(CryptoJS.enc.Utf8);
    return originalText;
}

// Called when room.html body loads
function initWS()
{
    const roomName = JSON.parse(document.getElementById('room-name').textContent);
    const username = JSON.parse(document.getElementById('username').textContent);
    const password = getCookie('password');

    // Initialize WebSocket
    const websocket_uri = 'ws://' + window.location.host + '/ws/chat/' + roomName + '/?username=' + encryptText(username, password);
    const chatSocket = new WebSocket(websocket_uri);

    // Called when user joins!
    chatSocket.onopen = function (e)
    {
        // Setting interval to detect disconnect
        const username = JSON.parse(document.getElementById('username').textContent);
        const password = getCookie('password');

        chatSocket.send(JSON.stringify({
            'type': 'join.message',
            'username': encryptText(username, password),
        }));
    }


    // Called when user leaves!
    chatSocket.onclose = function (e)
    {
        chatSocket.send(JSON.stringify({
            'type': 'leave.message',
            'username': encryptText(username, password)
        }));
    }
    // Called when user leaves!
    chatSocket.onerror = function (e)
    {
        chatSocket.send(JSON.stringify({
            'type': 'leave.message',
            'username': encryptText(username, password)
        }));
    }
    // Function that runs on message send
    chatSocket.onmessage = function (e)
    {
        // Adding number of messages
        var msgicon = document.getElementsByClassName('message')[0];
        var n_msg = document.getElementsByClassName('n-msg')[0];
        total_msg = parseInt(n_msg.innerText) + 1;
        total_msg = abbrNum(total_msg, 1);
        n_msg.innerText = total_msg.toString()
        n_msg.insertAdjacentElement('beforeend', msgicon);

        // Checking if it's a ping
        const data = JSON.parse(e.data);

        // Checking if it is system generated
        if (data.system)
        {   // Adding number of messages
            var usericon = document.getElementsByClassName('users')[0];
            var n_users = document.getElementsByClassName('n-users')[0];
            n_users.innerText = data.clients;
            n_users.insertAdjacentElement('beforeend', usericon);
            // Get username
            var username = decryptText(data.username, password);
            // Wrapping structure in div to get html content
            var wrapper = document.createElement('div');
            wrapper.innerHTML = data.structure;
            var div = wrapper.firstChild;
            // Adding username and other details to the DOM
            let now = new Date();
            div.firstElementChild.firstElementChild.nextElementSibling.firstElementChild.firstElementChild.nextElementSibling.innerText = new Intl.DateTimeFormat('en-US', { timeZone: 'UTC', timeStyle: 'short', dateStyle: 'short', }).format(now);
            // Adding decrypted data
            div.getElementsByClassName('user-texts')[0].firstElementChild.firstElementChild.innerText = username;
        }
        else
        {
            // Getting data from websocket
            var username = decryptText(data.username, password);
            var msg = decryptText(data.message, password);
            // Generating shortname
            var short_username = username.match(/(^\S\S?|\b\S)?/g).join("").match(/(^\S|\S$)?/g).join("").toUpperCase();
            // Wrapping structure in div to get html content
            var wrapper = document.createElement('div');
            wrapper.innerHTML = data.structure;
            var div = wrapper.firstChild;
            // Adding username and other details to the DOM
            div.firstElementChild.firstElementChild.firstElementChild.innerText = short_username;
            div.firstElementChild.firstElementChild.nextElementSibling.firstElementChild.firstElementChild.innerText = username;
            let now = new Date();
            div.firstElementChild.firstElementChild.nextElementSibling.firstElementChild.firstElementChild.nextElementSibling.innerText = new Intl.DateTimeFormat('en-US', { timeZone: 'UTC', timeStyle: 'short', dateStyle: 'short', }).format(now);
            // Adding decrypted data
            div.getElementsByClassName('user-texts')[0].innerText = msg;
        }
        // Making a shortusername for the PFP
        if (username.toLowerCase() == 'privmsg')
            var short_username = 'Priv\nMsg';
        else
            var short_username = username.match(/(^\S\S?|\b\S)?/g).join("").match(/(^\S|\S$)?/g).join("").toUpperCase();

        // Adding to chat area with auto scroll
        var chatarea = document.getElementById('chat-area');
        chatarea.appendChild(div);
        chatarea.scrollTop = chatarea.scrollHeight;
    };

    // If WebSocket closes
    chatSocket.onclose = function (e)
    {
        console.error('Chat socket closed unexpectedly');
    };

    document.querySelector('#chat-message-input').focus();

    // To set flag for shift!
    let keysPressed = {};
    document.querySelector('#chat-message-input').addEventListener('keydown', (event) =>
    {
        keysPressed[event.key] = true;
        // Enter was pressed
        if (event.key == 'Enter')
        {
            // Shift wasn't pressed so we can proceed with message
            if (!keysPressed['Shift'])
            {
                // Checking if message isn't empty, else send
                if (document.querySelector('#chat-message-input').value.trim() != '' && document.querySelector('#chat-message-input').value != "\n") 
                {
                    document.querySelector('#chat-message-input').blur();
                    // document.querySelector('#chat-message-input').value = "";
                    document.querySelector('#chat-message-submit').click();

                    // document.querySelector('#chat-message-input').disabled = false;
                    // document.querySelector('#chat-message-input').focus();
                }
                else
                {
                    return;
                }
            }
        }
    });

    document.querySelector('#chat-message-input').addEventListener('keyup', (event) =>
    {
        delete keysPressed[event.key];
    });
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
    // Sending message to websocket
    document.querySelector('#chat-message-submit').onclick = function (e)
    {
        const color = JSON.parse(document.getElementById('color').textContent);
        const messageInputDom = document.querySelector('#chat-message-input');
        const message = messageInputDom.value;
        // If message not empty
        if (message.trim() != '')
        {
            chatSocket.send(JSON.stringify({
                'message': encryptText(message, password),
                'username': encryptText(username, password),
                'color': color,
                'type': 'chat.message',
            }));
            messageInputDom.value = '';
        }
        document.getElementById('chat-message-input').removeAttribute("style");


    };

}

// Function to set cookies
function setCookie()
{
    const password = document.querySelector('#password').value;
    document.cookie = "password=" + password;
}

// Function to make dynamic text area
function autoResize()
{
    if (this.scrollHeight >= 150)
    {
        this.style.overflowY = 'auto';
    }
    else
    {
        this.style.height = 'auto';
        this.style.height = this.scrollHeight + 'px';
    }

}
var textarea = document.getElementById('chat-message-input');
textarea.addEventListener('input', autoResize, false);


// Send button listener
// function resetSize()
// {
//     document.querySelector('#chat-message-submit').click();

//     document.getElementById('chat-message-input').removeAttribute("style");
// }
// send = document.getElementById('chat-message-submit');
// send.addEventListener('click', resetSize);

// Readable number
function abbrNum(number, decPlaces)
{
    decPlaces = Math.pow(10, decPlaces);
    var abbrev = ["k", "m", "b", "t"];
    for (var i = abbrev.length - 1; i >= 0; i--)
    {
        var size = Math.pow(10, (i + 1) * 3);
        if (size <= number)
        {
            number = Math.round(number * decPlaces / size) / decPlaces;
            if ((number == 1000) && (i < abbrev.length - 1))
            {
                number = 1;
                i++;
            }
            number += abbrev[i];
            break;
        }
    }
    return number;
}

function copyURL()
{
    var dummy = document.createElement('input'),
        text = window.location.href;
    document.body.appendChild(dummy);
    dummy.value = text;
    dummy.select();
    document.execCommand('copy');
    document.body.removeChild(dummy);
    alert("Copied the URL!");
}