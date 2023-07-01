import { Component, OnInit } from '@angular/core';
import {Buffer} from 'buffer';
import { timeLog } from 'console';


@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})

export class HomeComponent implements OnInit {
  password: string = "";
  encrypted = "";
  plaintext = "";
  decrypted="";
  totp = require('totp-generator');
  code = "";
  duration=0;

  ngOnInit(){
    // each second :
    setInterval(()=> { this.generateCode() }, 500);


  }

  generateCode(){
    console.log("generate code")
       this.duration = 30 - Math.floor(Date.now() / 1000 % 30);
      this.code=this.totp("JBSWY3DPEHPK3PXP");
  }

  

 login(){
    const crypto = new Crypto(this.password);
    crypto.encrypt(this.plaintext).then(encrypted=>{
      this.encrypted = encrypted;
      crypto.decrypt(this.encrypted).then(decrypted=>{
        if(decrypted == null){
          this.decrypted = "Wrong key"
        } else {
          this.decrypted = decrypted;
        }
       
      })
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

  async encrypt(plaintext:string) :Promise<string>{
    const enc = new TextEncoder();
    const plaintextBytes = enc.encode(plaintext);
    const ivBytes = window.crypto.getRandomValues(new Uint8Array(12))
    const saltBytes = window.crypto.getRandomValues(new Uint8Array(16))
    const key = await this.deriveKey(saltBytes);
  
    const encoded_encrypted = await window.crypto.subtle.encrypt({ name: "AES-GCM", iv: ivBytes }, key, plaintextBytes);
    return  Buffer.from(encoded_encrypted).toString('base64') + "," + Buffer.from(ivBytes).toString('base64') + ","+ Buffer.from(saltBytes).toString('base64');
  }

  async decrypt(encrypted:string) : Promise<string | null>{
    const part = encrypted.split(",")
    if (part.length != 3){
      return null;
    }
    try{
      const cipher = Buffer.from(part[0], 'base64');
      const iv = Buffer.from(part[1], 'base64');
      const salt = Buffer.from(part[2], 'base64');
      const key = await this.deriveKey(salt);
      const encoded_decrypted = await window.crypto.subtle.decrypt({ name: "AES-GCM", iv: iv }, key, cipher);
      return Buffer.from(encoded_decrypted).toString("utf-8");
    } catch {
      return null
    }
    



  }
  

  

  

}
