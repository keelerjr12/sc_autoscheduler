import { Component } from '@angular/core';
import { Schedule } from 'src/app/core/models/schedule.model';
import { ScheduleAPIService } from 'src/app/core/services/schedule-api.service';

function getIconStringFromStatus(status: string) {
  switch (status) {
    case 'Completed':
      return 'bg-success';
    case 'Pending':
      return 'bg-info';
  };

  return 'bg-warning';
}

export class ScheduleViewModel {
  name: string;
  startDate: string;
  endDate: string;
  submissionDateTime: string;
  status: string;
  icon: string;

  constructor(private schedule: Schedule) {
    this.name = schedule.name;
    this.startDate = schedule.start_date;
    this.endDate = schedule.end_date;
    this.submissionDateTime = schedule.submission_date_time;
    this.status = schedule.status;
    this.icon = getIconStringFromStatus(this.status);
  }
}

@Component({
  selector: 'sc-schedule-page',
  templateUrl: './schedule-page.component.html',
  styleUrls: ['./schedule-page.component.css']
})
export class SchedulePageComponent {

  schedules: ScheduleViewModel[] = []

  currentTab: number = 0;
  MAX_TABS: number = 4;

  constructor(private scheduleAPI: ScheduleAPIService) { }

  ngOnInit() {
    this.scheduleAPI.getSchedules().subscribe(scheduleDTO => {
      this.schedules = scheduleDTO.map(schedule => { return new ScheduleViewModel(schedule) });
    });
  }

  prevNext(inc: number) {
    this.currentTab += inc;

    if (this.currentTab < 0) {
      this.currentTab = 0;
    }

    if (this.currentTab >= this.MAX_TABS) {
      this.currentTab = this.MAX_TABS - 1;
    }
  }
}
