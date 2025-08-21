import { TestBed } from '@angular/core/testing';

import { GlobalConfigurationService } from './global-configuration.service';

describe('GlobalConfigurationService', () => {
  let service: GlobalConfigurationService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(GlobalConfigurationService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
