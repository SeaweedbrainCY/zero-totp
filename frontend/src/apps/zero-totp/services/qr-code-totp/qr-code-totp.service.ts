import { Injectable } from '@angular/core';
import { sanitize } from '../../../../shared/Utils/utils';

@Injectable({
  providedIn: 'root'
})
export class QrCodeTOTP {
    private label:string | undefined = undefined;
    private secret:string | undefined = undefined;



    getLabel():string | undefined{
        return this.label
    }

    setLabel(label:string){
        this.label = sanitize(label) || '';
    }

    getSecret():string|undefined{
        return this.secret;
    }

    setSecret(secret : string){
        this.secret = sanitize(secret) || '';
    }

}
