import { Injectable } from '@angular/core';
import { Utils } from '../Utils/utils';

@Injectable({
  providedIn: 'root'
})
export class QrCodeTOTP {
    private label:string | undefined = undefined;
    private secret:string | undefined = undefined;
    private utils = new Utils();



    getLabel():string | undefined{
        return this.label
    }

    setLabel(label:string){
        this.label =  this.utils.sanitize(label) || '';
    }

    getSecret():string|undefined{
        return this.secret;
    }

    setSecret(secret : string){
        this.secret = this.utils.sanitize(secret) || '';
    }
    
}
