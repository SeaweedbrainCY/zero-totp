import { faColonSign } from '@fortawesome/free-solid-svg-icons';
import {Buffer} from 'buffer';
import { environment } from 'src/environments/environment';


export class Crypto {

    pbkdf2_iterations = 700000;
    

    generateKeyMaterial(password: string) {
        const enc = new TextEncoder();
        return window.crypto.subtle.importKey("raw", enc.encode(password), "PBKDF2", false, ["deriveBits", "deriveKey"]);
    }

    generateRandomSalt(): string {
        return Buffer.from(window.crypto.getRandomValues(new Uint8Array(16))).toString('base64');
    }

    generateZKEKey():string {
        return Buffer.from(window.crypto.getRandomValues(new Uint8Array(32))).toString('base64');
    }



    async deriveKey(salt: string, password: string): Promise<CryptoKey> {
        const key_material = await this.generateKeyMaterial(password);
        const saltBytes = Buffer.from(salt, 'base64');
        const key = window.crypto.subtle.deriveKey(
            {
                name: "PBKDF2",
                salt: saltBytes,
                iterations: this.pbkdf2_iterations,
                hash: "SHA-256",
            },
            key_material,
            { name: "AES-GCM", length: 256 },
            true,
            ["encrypt", "decrypt"]
        );
        return key;
    }

    async encrypt(plaintext: string, key: CryptoKey): Promise<string> {
        const enc = new TextEncoder();
        const plaintextBytes = enc.encode(plaintext);
        const ivBytes = window.crypto.getRandomValues(new Uint8Array(12))
        const encoded_encrypted = await window.crypto.subtle.encrypt({ name: "AES-GCM", iv: ivBytes }, key, plaintextBytes);
        return Buffer.from(encoded_encrypted).toString('base64') + "," + Buffer.from(ivBytes).toString('base64');
    }

    async decrypt(encrypted: string, key: CryptoKey): Promise<string | null> {
        const part = encrypted.split(",")
        if (part.length < 2 ) {
            return null;
        }
        try {
            const cipher = Buffer.from(part[0], 'base64');
            const iv = Buffer.from(part[1], 'base64');
            const encoded_decrypted = await window.crypto.subtle.decrypt({ name: "AES-GCM", iv: iv }, key, cipher);
            return Buffer.from(encoded_decrypted).toString("utf-8");
        } catch(error) {
            console.log(error)
            return null
        }
    }

    async hashPassphrase(password: string, salt:string): Promise<string | null>{
        const passwordBytes = Buffer.from(password, 'utf-8');
        const saltBytes = Buffer.from(salt, 'base64');
        const hash = await window.crypto.subtle.digest("SHA-256", Buffer.concat([passwordBytes, saltBytes]));
        return Buffer.from(hash).toString('base64');
    }

    async verifySignature(vault_b64:string, signature_bd64:string):Promise<boolean>{
          const textEncoder = new TextEncoder();
          let encoded_vault = textEncoder.encode(vault_b64);
          let encoded_signature = Buffer.from(signature_bd64, "base64");
          const publicKey = await this.importPublicKey(environment.API_public_key)
          const result = await window.crypto.subtle.verify(
              "RSASSA-PKCS1-v1_5",
              publicKey,
              encoded_signature,
              encoded_vault,
          );
          return result
      }

      async importPublicKey(publicKeyPEM: string): Promise<CryptoKey> {
        const publicKeyDER = atob(publicKeyPEM.replace(/-----BEGIN PUBLIC KEY-----|-----END PUBLIC KEY-----/g, ''));
      
        const publicKeyBuffer = this.str2ab(publicKeyDER);
        console.log("publicKeyBuffer: " + publicKeyBuffer)
      
        const publicKey = await crypto.subtle.importKey(
          'spki',
          publicKeyBuffer,
          {
            name: 'RSASSA-PKCS1-v1_5',
            hash: 'SHA-256',
          },
          true,
          ['verify']
        );
        console.log("publicKey: " + publicKey)
        return publicKey;
      }

    str2ab(str:string) {
        const buf = new ArrayBuffer(str.length);
        const bufView = new Uint8Array(buf);
        for (let i = 0, strLen = str.length; i < strLen; i++) {
          bufView[i] = str.charCodeAt(i);
        }
        return buf;
      }
}