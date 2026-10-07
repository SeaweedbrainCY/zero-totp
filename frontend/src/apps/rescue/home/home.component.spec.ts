import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RescueHomeComponent } from './home.component';

describe('HomeComponent', () => {
  let component: RescueHomeComponent;
  let fixture: ComponentFixture<RescueHomeComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
    declarations: [RescueHomeComponent]
});
    fixture = TestBed.createComponent(RescueHomeComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
