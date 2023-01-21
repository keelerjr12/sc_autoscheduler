import { TestBed } from '@angular/core/testing';

import { ScheduleAPIService } from './schedule-api.service';

describe('ScheduleAPIService', () => {
  let service: ScheduleAPIService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(ScheduleAPIService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
