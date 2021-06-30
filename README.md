# PrivMsg
E2E Burner Chat Rooms - (Readable Readme soon)

# What is PrivMsg?
PrivMsg is a Free and Open Source Software that is also self-hostable. It is built to be an instant messaging and burn note service. It is written and built with django channels and mongodb.

PrivMsg uses AES-256 bit encryption to encrypt your messages and notes. PrivMsg also features a burn note functionality. Every burn note link comes with two parts - the identifier and a password which is separated by a semi colon. PrivMsg only stores the identifier, while the password which is used to encrypt the link, it is never stored in the database.

# Technologies used
- Django
- Django Channels for WebSockets

# Credits

This project wouldn't have been possible without the contributions of the following people:

[MarkisDev](https://github.com/MarkisDev)  
[Gokul1here](https://github.com/Gokul1here)  
[V01D0](https://github.com/V01D0)
