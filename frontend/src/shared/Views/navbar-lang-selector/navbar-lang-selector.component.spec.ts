import { ComponentFixture, TestBed } from '@angular/core/testing';

import { NavbarLangSelectorComponent } from './navbar-lang-selector.component';

describe('NavbarLangSelectorComponent', () => {
  let component: NavbarLangSelectorComponent;
  let fixture: ComponentFixture<NavbarLangSelectorComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [NavbarLangSelectorComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(NavbarLangSelectorComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
