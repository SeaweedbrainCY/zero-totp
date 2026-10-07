import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RescueNavbarComponent } from './rescue-navbar.component';

describe('RescueNavbarComponent', () => {
  let component: RescueNavbarComponent;
  let fixture: ComponentFixture<RescueNavbarComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RescueNavbarComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(RescueNavbarComponent);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
