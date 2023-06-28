import { Component } from '@angular/core';
import {Buffer} from 'buffer';


@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})
export class HomeComponent {
  password: string = "";
  encrypted = "";
  plaintext = "";
  salt="";

 login(){
    const crypto = new Crypto(this.password);
    this.salt = Buffer.from(window.crypto.getRandomValues(new Uint8Array(16))).toString('base64');
    crypto.encrypt(this.plaintext, this.salt).then(encrypted=>{
      this.encrypted = encrypted;
    });
 }


}

export class Crypto {
  password: string;

  constructor(password: string) {
    this.password = password;
  }

   generateKeyMaterial(){
    const enc = new TextEncoder();
    return window.crypto.subtle.importKey("raw", enc.encode(this.password),"PBKDF2",false,["deriveBits", "deriveKey"]);
  }

  async deriveKey(salt:BufferSource){
    const key_material = await this.generateKeyMaterial();
    const key = window.crypto.subtle.deriveKey(
      {
        name: "PBKDF2",
        salt,
        iterations: 100000,
        hash: "SHA-256",
      },
      key_material,
      { name: "AES-GCM", length: 256 },
      true,
      ["encrypt", "decrypt"]
    );
    return key;
  }

  async encrypt(plaintext:string, salt:string) :Promise<string>{
    const enc = new TextEncoder();
    const plaintextBytes = enc.encode(plaintext);
    const ivBytes = window.crypto.getRandomValues(new Uint8Array(12))
    const saltBytes = Buffer.from(salt, 'base64');
    const key = await this.deriveKey(saltBytes);
  
    const encoded_encrypted = await window.crypto.subtle.encrypt({ name: "AES-GCM", iv: ivBytes }, key, plaintextBytes);
    return  Buffer.from(encoded_encrypted).toString('base64') + "," + Buffer.from(ivBytes).toString('base64') + ","+ Buffer.from(saltBytes).toString('base64');
  }
  

  

  

}
