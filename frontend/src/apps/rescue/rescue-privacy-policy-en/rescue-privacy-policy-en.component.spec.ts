import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RescuePrivacyPolicyEnComponent } from './rescue-privacy-policy-en.component';

describe('RescuePrivacyPolicyEnComponent', () => {
  let component: RescuePrivacyPolicyEnComponent;
  let fixture: ComponentFixture<RescuePrivacyPolicyEnComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RescuePrivacyPolicyEnComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(RescuePrivacyPolicyEnComponent);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
