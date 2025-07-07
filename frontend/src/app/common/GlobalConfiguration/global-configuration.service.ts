import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class GlobalConfigurationService {
  private is_google_drive_backup_enabled: boolean | undefined;
  constructor(
    private http: HttpClient
  ) { 

  }


  public is_google_drive_enabled_on_this_tenant():Promise<boolean> {
    return new Promise((resolve, _) => {
      if (this.is_google_drive_backup_enabled !== undefined) {
        resolve(this.is_google_drive_backup_enabled);
        return;
      }
      this.http.get("/api/v1/backup/server/options", {withCredentials:true, observe: 'response'}).subscribe({
        next : (response) => { 
          const data = response.body as { google_drive_enabled: boolean };
          this.is_google_drive_backup_enabled =  data.google_drive_enabled;
          resolve(data.google_drive_enabled);
        }, error: (error) => {
          console.log(error);
          resolve(false);
      }});
    });

  }

  public setGoogleDriveBackupEnabled(enabled: boolean) {
    this.is_google_drive_backup_enabled = enabled;
  }
}
