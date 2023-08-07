import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DevComponent } from './dev.component';

describe('DevComponent', () => {
  let component: DevComponent;
  let fixture: ComponentFixture<DevComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [DevComponent]
    });
    fixture = TestBed.createComponent(DevComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
