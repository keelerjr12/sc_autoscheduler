import { Component } from '@angular/core';
import { ShellFlyingLine } from 'src/app/core/models/shell_flying_line.model';
import { ScheduleShellAPIService } from 'src/app/core/services/schedule-shell-api.service';
import { BuildPageShellLine } from '../models/build-page-shell-line.model';
import { TabItem } from '../models/tabitem.model';

@Component({
  selector: 'sc-schedule-build-page',
  templateUrl: './schedule-build-page.component.html',
  styleUrls: ['./schedule-build-page.component.css']
})
export class ScheduleBuildPageComponent {

  currentTabIdx: number = 0;

  tabs: TabItem[] = [];
  currentTab: TabItem = this.tabs[0];

  startDate: Date = new Date(2022, 11, 5);
  endDate: Date = new Date(2022, 11, 9);
  currDate: Date = new Date(2022, 11, 5);
  currDateStr: string = this.currDate.toDateString();
  
  shell_lines: BuildPageShellLine[] = [];
  cols: any[] = [];


  constructor(private scheduleShellAPI: ScheduleShellAPIService) { }

  ngOnInit() {
    this.tabs = [
      {label: 'Start'},
      {label: 'Flying Shell'},
      {label: 'Duty Shell'},
      {label: 'Build'}
    ];

    this.currentTab = this.tabs[0];

    this.cols = [
      { field: 'num', header: 'Blk'},
      { field: 'takeoff_time', header: 'Takeoff'},
      { field: 'assigned_org', header: 'Assigned Org'}
    ];
  }

  prevNext(inc: number) {
    console.log(this.startDate);
    console.log(this.endDate);

    if (this.startDate == undefined || this.endDate == undefined) {
      console.log('Please select a date');
      return;
    }

    if (this.onStartPage() && inc === 1)
    {
      this.loadFlyingShell();
    }

    this.currentTabIdx += inc;

    if (this.currentTabIdx < 0) {
      this.currentTabIdx = 0;
    }

    if (this.currentTabIdx >= this.tabs.length) {
      this.currentTabIdx = this.tabs.length - 1;
    }

    this.currentTab = this.tabs[this.currentTabIdx];
  }

  prevNextDay(inc: number) {
    this.currDate.setDate(this.currDate.getDate() + inc);
    this.currDateStr = this.currDate.toDateString();
  
    this.loadFlyingShell();
  }

  onStartPage(): boolean {
    return this.currentTabIdx === 0
  }

  loadFlyingShell(): void {
    this.scheduleShellAPI.getFlyingShell(this.currDate).subscribe(shell => {
      console.log(shell);
      this.shell_lines = shell.map(line => new BuildPageShellLine(line));
      console.log(this.shell_lines);
    });
  }
}
