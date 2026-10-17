import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RescuePrivacyPolicyComponent } from './rescue-privacy-policy.component';

describe('RescuePrivacyPolicyComponent', () => {
  let component: RescuePrivacyPolicyComponent;
  let fixture: ComponentFixture<RescuePrivacyPolicyComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RescuePrivacyPolicyComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(RescuePrivacyPolicyComponent);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
