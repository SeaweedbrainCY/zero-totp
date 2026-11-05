import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MobileHomeComponent } from './mobile-home.component';

describe('MobileHomeComponent', () => {
  let component: MobileHomeComponent;
  let fixture: ComponentFixture<MobileHomeComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [MobileHomeComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(MobileHomeComponent);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
