"use strict";
import CryptoJS from "crypto-js";

function EncryptText(text, password) {
  return CryptoJS.AES.encrypt(text, password).toString();
}

function decryptText(ciphertext, password) {
  const bytes = CryptoJS.AES.decrypt(ciphertext, password);
  const originalText = bytes.toString(CryptoJS.enc.Utf8);
  return originalText;
}
