import { Component } from '@angular/core';
import { Schedule } from 'src/app/core/models/schedule.model';
import { ScheduleAPIService } from 'src/app/core/services/schedule-api.service';

@Component({
  selector: 'sc-schedule-page',
  templateUrl: './schedule-page.component.html',
  styleUrls: ['./schedule-page.component.css']
})
export class SchedulePageComponent {
  schedules: Schedule[] = []
  constructor(private scheduleAPI: ScheduleAPIService) { }

  ngOnInit() {
    this.scheduleAPI.getSchedules().subscribe(scheduleDTO => {
      this.schedules = scheduleDTO;
    });
  }
}
