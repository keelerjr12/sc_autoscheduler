import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { ScheduleRoutingModule } from './schedule-routing.module';
import { SchedulePageComponent } from './schedule-page/schedule-page.component';
import { ScheduleListPageComponent } from './schedule-list-page/schedule-list-page.component';
import { ScheduleBuildPageComponent } from './schedule-build-page/schedule-build-page.component';


@NgModule({
  declarations: [
    SchedulePageComponent,
    ScheduleListPageComponent,
    ScheduleBuildPageComponent
  ],
  imports: [
    CommonModule,
    ScheduleRoutingModule
  ]
})
export class ScheduleModule { }
