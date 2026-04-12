import { Component, OnInit, signal, WritableSignal } from '@angular/core';
import { TranslateService } from '@ngx-translate/core';
import {faCircleNotch, faArrowUpRightFromSquare, faCircleXmark }  from '@fortawesome/free-solid-svg-icons';
import { HttpClient, HttpHeaders } from '@angular/common/http';

@Component({
    selector: 'app-privacy-policy',
    templateUrl: './privacy-policy.component.html',
    styleUrls: ['./privacy-policy.component.css'],
    standalone: false
})
export class PrivacyPolicyComponent implements OnInit {

    current_language:string = localStorage.getItem('language') || 'en-uk';
    privacy_policy_url_base_url = "/api/v1/privacy-policy?lang="
    privacy_policy_url = ""
    is_privacy_policy_loaded = signal(false);
    loading_error = signal(false);
    faCircleNotch=faCircleNotch;
    faArrowUpRightFromSquare=faArrowUpRightFromSquare;
    faCircleXmark=faCircleXmark;
    privacy_policy_md: WritableSignal<string | undefined> = signal(undefined);

    constructor(
        public translate: TranslateService,
        private http: HttpClient
    ){
        
       this.langChanged();
       this.translate.onLangChange.subscribe(() => {
            this.langChanged();
        });


    }

    ngOnInit(): void {
        this.load_privacy_policy();
    }

    load_privacy_policy() {
        this.is_privacy_policy_loaded.set(false);
        this.loading_error.set(false);

        this.http.get(this.privacy_policy_url, {observe:'response', responseType: 'text'})
            .subscribe({
                next: (response) => {
                    if(response.status == 200){
                        if(response.headers.get('Content-Type')?.includes('text/markdown')){
                            this.privacy_policy_md.set(response.body!);
                        } else {
                            console.error('Unexpected content type:', response.headers.get('Content-Type'));
                            this.loading_error.set(true);
                            return;
                        }
                    } else {
                        console.error('Unexpected response status:', response.status);
                        this.loading_error.set(true);
                        return;
                    }
                    this.is_privacy_policy_loaded.set(true);
                },
                error: (error) => {
                    console.error('Error loading privacy policy:', error);
                    this.loading_error.set(true);
                }
            });
    }

    langChanged() {
         if (this.translate.currentLang === 'fr-fr') {
            this.privacy_policy_url = this.privacy_policy_url_base_url + 'fr';
            this.load_privacy_policy();
        } else {
            this.privacy_policy_url = this.privacy_policy_url_base_url + 'en';
            this.load_privacy_policy();
        }
    }

}
