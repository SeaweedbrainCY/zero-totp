import { TestBed } from '@angular/core/testing';

import { DisplayPreferencesService } from './display-preferences.service';

describe('DisplayPreferencesService', () => {
  let service: DisplayPreferencesService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(DisplayPreferencesService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
