import {Buffer} from 'buffer';
import { timeLog } from 'console';


export class Crypto {

    generateKeyMaterial(password: string) {
        const enc = new TextEncoder();
        return window.crypto.subtle.importKey("raw", enc.encode(password), "PBKDF2", false, ["deriveBits", "deriveKey"]);
    }

    generateRandomSalt(): string {
        return Buffer.from(window.crypto.getRandomValues(new Uint8Array(16))).toString('base64');
    }



    async deriveKey(salt: string, password: string): Promise<CryptoKey> {
        const key_material = await this.generateKeyMaterial(password);
        const saltBytes = Buffer.from(salt, 'base64');
        const key = window.crypto.subtle.deriveKey(
            {
                name: "PBKDF2",
                salt: saltBytes,
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

    async encrypt(plaintext: string, key: CryptoKey, salt: string): Promise<string> {
        const enc = new TextEncoder();
        const plaintextBytes = enc.encode(plaintext);
        const ivBytes = window.crypto.getRandomValues(new Uint8Array(12))
        const saltBytes = Buffer.from(salt, 'base64');
        const encoded_encrypted = await window.crypto.subtle.encrypt({ name: "AES-GCM", iv: ivBytes }, key, plaintextBytes);
        return Buffer.from(encoded_encrypted).toString('base64') + "," + Buffer.from(ivBytes).toString('base64') + "," + Buffer.from(saltBytes).toString('base64');
    }

    async decrypt(encrypted: string, key: CryptoKey): Promise<string | null> {
        const part = encrypted.split(",")
        if (part.length != 3) {
            return null;
        }
        try {
            const cipher = Buffer.from(part[0], 'base64');
            const iv = Buffer.from(part[1], 'base64');
            const encoded_decrypted = await window.crypto.subtle.decrypt({ name: "AES-GCM", iv: iv }, key, cipher);
            return Buffer.from(encoded_decrypted).toString("utf-8");
        } catch {
            return null
        }
    }






}