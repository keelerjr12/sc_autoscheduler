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
  selector: 'sc-schedule-list-page',
  templateUrl: './schedule-list-page.component.html',
  styleUrls: ['./schedule-list-page.component.css']
})
export class ScheduleListPageComponent {

  schedules: ScheduleViewModel[] = []

  constructor(private scheduleAPI: ScheduleAPIService) { }

  ngOnInit() {
    this.scheduleAPI.getSchedules().subscribe(scheduleDTO => {
      this.schedules = scheduleDTO.map(schedule => { return new ScheduleViewModel(schedule) });
    });
  }
}
