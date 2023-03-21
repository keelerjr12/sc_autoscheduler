import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { ScheduleRoutingModule } from './schedule-routing.module';
import { SchedulePageComponent } from './schedule-page/schedule-page.component';
import { ScheduleListPageComponent } from './schedule-list-page/schedule-list-page.component';
import { ScheduleBuildPageComponent } from './schedule-build-page/schedule-build-page.component';

import { TableModule } from 'primeng/table'
import { FormsModule } from '@angular/forms';

@NgModule({
  declarations: [
    SchedulePageComponent,
    ScheduleListPageComponent,
    ScheduleBuildPageComponent
  ],
  imports: [
    CommonModule,
    FormsModule,
    ScheduleRoutingModule,
    TableModule
  ]
})
export class ScheduleModule { }
