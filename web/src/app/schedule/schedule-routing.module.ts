import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { ScheduleBuildPageComponent } from './schedule-build-page/schedule-build-page.component';
import { ScheduleListPageComponent } from './schedule-list-page/schedule-list-page.component';
import { SchedulePageComponent } from './schedule-page/schedule-page.component';

const routes: Routes = [
  {
    path: 'nav',
    component: SchedulePageComponent
  },
  {
    path: '',
    component: ScheduleListPageComponent
  },
  {
    path: 'build',
    component: ScheduleBuildPageComponent
  }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class ScheduleRoutingModule { }
