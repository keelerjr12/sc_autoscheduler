import { TestBed } from '@angular/core/testing';

import { PersonnelAPIService } from './personnel-api.service';

describe('PersonnelAPIService', () => {
  let service: PersonnelAPIService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(PersonnelAPIService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
