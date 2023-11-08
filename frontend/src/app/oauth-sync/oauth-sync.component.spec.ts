import { ComponentFixture, TestBed } from '@angular/core/testing';

import { OauthSyncComponent } from './oauth-sync.component';

describe('OauthSyncComponent', () => {
  let component: OauthSyncComponent;
  let fixture: ComponentFixture<OauthSyncComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [OauthSyncComponent]
    });
    fixture = TestBed.createComponent(OauthSyncComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
