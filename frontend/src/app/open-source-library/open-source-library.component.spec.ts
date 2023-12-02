import { ComponentFixture, TestBed } from '@angular/core/testing';

import { OpenSourceLibraryComponent } from './open-source-library.component';

describe('OpenSourceLibraryComponent', () => {
  let component: OpenSourceLibraryComponent;
  let fixture: ComponentFixture<OpenSourceLibraryComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [OpenSourceLibraryComponent]
    });
    fixture = TestBed.createComponent(OpenSourceLibraryComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
