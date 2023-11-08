import { Component, OnInit } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { faCircleNotch } from '@fortawesome/free-solid-svg-icons';


@Component({
  selector: 'app-callback',
  templateUrl: './callback.component.html',
  styleUrls: ['./callback.component.css']
})
export class CallbackComponent implements OnInit{
  errorMessage = '';
  faCircleNotch = faCircleNotch;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    ) { }

  ngOnInit() {
    this.route.queryParams.subscribe(params => {
      const state = params['state'];
      const sessionState = sessionStorage.getItem('oauth_state');
      if(sessionState != '' && sessionState != null && state == sessionState){
        const status = params['status'];
        if (status == "success") {
          this.router.navigate(["/login/oauth"], {relativeTo:this.route.root});
        } else {
          this.errorMessage = 'Impossible to synchronize your vault. Please try again.';
        }
      } else {
        this.errorMessage = 'Impossible to identify your synchronization request. Please try again.';
      }
    });
  }

}
