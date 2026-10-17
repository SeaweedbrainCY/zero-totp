import { Component, OnInit, signal, ChangeDetectionStrategy } from '@angular/core';
import { Router, ActivatedRoute, RouterLink } from '@angular/router';
import { faCircleNotch, faArrowUpRightFromSquare } from '@fortawesome/free-solid-svg-icons';
import { FaIconComponent } from '@fortawesome/angular-fontawesome';
import { NgClass } from '@angular/common';
import { TranslatePipe } from '@ngx-translate/core';


@Component({
    selector: 'app-callback',
    templateUrl: './callback.component.html',
    styleUrls: ['./callback.component.css'],
    changeDetection: ChangeDetectionStrategy.OnPush,
    imports: [
        FaIconComponent,
        NgClass,
        RouterLink,
        TranslatePipe,
    ],
})
export class CallbackComponent implements OnInit{
  errorMessage = signal('');
  faCircleNotch = faCircleNotch;
  faArrowUpRightFromSquare = faArrowUpRightFromSquare;
  google_drive_refresh_token_error_display_modal_active = signal(false);

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
          this.errorMessage.set('Impossible to synchronize your vault. Please try again.');
        }
      } else if (status=="refresh-token-error"){
          this.google_drive_refresh_token_error_display_modal_active.set(true);
      } else {
        this.errorMessage.set('Impossible to identify your synchronization request. Please try again.');
      }
    });
  }

}