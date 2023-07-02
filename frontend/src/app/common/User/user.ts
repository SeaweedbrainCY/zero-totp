export class User {
    id:number| null =null;;
    key:CryptoKey| null =null;;
    salt:string| null =null;;
    vault:[string:string] | null =null;
}
