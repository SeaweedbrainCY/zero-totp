export class Utils {

    constructor(){}
      

    sanitize(unsafe_str:string|null) : string |null {
        if(unsafe_str == null){
            return null;
        }
        return unsafe_str.replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;').replaceAll("'", '&#039;').replaceAll('/', '&#x2F;').replaceAll('`', '&#x60;').replaceAll('=', '&#x3D;');
    }

    passwordSanitize(unsafe_str:string|null) : string |null {
        if(unsafe_str == null){
            return null;
        }
        return unsafe_str.replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;').replaceAll("'", '&#039;').replaceAll('`', '&#x60;');
    }
}
