import { Component } from '@angular/core';
import { ScheduleShellAPIService } from 'src/app/core/services/schedule-shell-api.service';

@Component({
  selector: 'sc-schedule-build-page',
  templateUrl: './schedule-build-page.component.html',
  styleUrls: ['./schedule-build-page.component.css']
})
export class ScheduleBuildPageComponent {

  currentTab: number = 0;
  MAX_TABS: number = 4;

  constructor(private scheduleShellAPI: ScheduleShellAPIService) { }

  prevNext(inc: number) {

    if (this.onStartPage() && inc === 1)
    {
      this.loadFlyingShell();
    }

    this.currentTab += inc;

    if (this.currentTab < 0) {
      this.currentTab = 0;
    }

    if (this.currentTab >= this.MAX_TABS) {
      this.currentTab = this.MAX_TABS - 1;
    }
  }

  onStartPage(): boolean {
    return this.currentTab === 0
  }

  loadFlyingShell(): void {
    console.log('hey');
    this.scheduleShellAPI.getFlyingShell().subscribe(shell =>
      console.log(shell));
  }
}
