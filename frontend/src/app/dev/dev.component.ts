import { Component } from '@angular/core';
import { Crypto } from '../common/Crypto/crypto';
import {Buffer} from 'buffer'

@Component({
  selector: 'app-dev',
  templateUrl: './dev.component.html',
  styleUrls: ['./dev.component.css']
})
export class DevComponent {
  salt=""
  passphrase=""
  derivedKey=""
  time=0
  prng=0
  seedrandom = require('seedrandom')
  EC = require('elliptic').ec
  ec = new this.EC('secp256k1');
  privateKey=""
  publicKey=""

  constructor(private crypto:Crypto) {
     
   }
  
  derive(){
    const start = Date.now()
    this.crypto.deriveKey(this.salt, this.passphrase).then((key)=>{
       window.crypto.subtle.exportKey("raw", key).then((keyRaw)=>{
        // convert in hex :
        this.derivedKey = Buffer.from(keyRaw).toString('hex')

        this.time = (Date.now() - start)/1000
        
    });
  });
}

generateSalt(){
  this.salt = this.crypto.generateRandomSalt()
}

generatePRNG(){
  this.prng = this.seedrandom(this.derivedKey).double()
}

generateEcdsaKeyPair(){
  const keyPair = this.ec.genKeyPair({ entropy: this.derivedKey });
  this.publicKey = keyPair.getPublic('hex')
  this.privateKey = keyPair.getPrivate('hex');

}

}
