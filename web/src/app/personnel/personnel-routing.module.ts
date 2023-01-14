import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { PersonnelPageComponent } from './personnel-page/personnel-page.component';

const routes: Routes = [
  {
    path: '',
    component: PersonnelPageComponent
  }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class PersonnelRoutingModule { }
