import { Component, OnInit } from '@angular/core';
import {Crypto} from '../common/Crypto/crypto';


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
       this.duration = 30 - Math.floor(Date.now() / 1000 % 30);
      this.code=this.totp("JBSWY3DPEHPK3PXP");
  }

  

 login(){
    const crypto = new Crypto();
    const salt = crypto.generateRandomSalt();
    crypto.deriveKey(salt, this.password).then(key=>{
      crypto.encrypt(this.plaintext, key, salt).then(encrypted=>{
        this.encrypted = encrypted;
        crypto.decrypt(this.encrypted, key).then(decrypted=>{
          if(decrypted == null){
            this.decrypted = "Wrong key"
          } else {
            this.decrypted = decrypted;
          }
        
        })
      });
    });
    
 }


}

