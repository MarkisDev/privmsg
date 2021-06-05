
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
