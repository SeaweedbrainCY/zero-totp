export class User {
    id:number;
    key:CryptoKey;
    salt:string;
    vault:[string:string] | null =null;

    constructor(id:number, key:CryptoKey, salt:string){
        this.id = id;
        this.key = key;
        this.salt = salt;
    }
}
