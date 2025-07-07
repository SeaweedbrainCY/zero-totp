import { Component, OnInit } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { faCircleNotch, faArrowUpRightFromSquare } from '@fortawesome/free-solid-svg-icons';


@Component({
    selector: 'app-callback',
    templateUrl: './callback.component.html',
    styleUrls: ['./callback.component.css'],
    standalone: false
})
export class CallbackComponent implements OnInit{
  errorMessage = '';
  faCircleNotch = faCircleNotch;
  faArrowUpRightFromSquare=faArrowUpRightFromSquare;
  google_drive_refresh_token_error_display_modal_active = false;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    ) { }

  ngOnInit() {
    this.route.queryParams.subscribe(params => {
      const state = params['state'];
      const status = params['status'];
      const sessionState = sessionStorage.getItem('oauth_state');
      if(sessionState != '' && sessionState != null && state == sessionState){
        if (status == "success") {
          this.router.navigate(["/login/oauth"], {relativeTo:this.route.root});
        } else {
          this.errorMessage = 'Impossible to synchronize your vault. Please try again.';
        }
      } else if (status=="refresh-token-error"){
          this.google_drive_refresh_token_error_display_modal_active = true;
      } else {
        this.errorMessage = 'Impossible to identify your synchronization request. Please try again.';
      }
    });
  }

}
