import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { PersonnelRoutingModule } from './personnel-routing.module';
import { PersonnelPageComponent } from './personnel-page/personnel-page.component';


@NgModule({
  declarations: [
    PersonnelPageComponent
  ],
  imports: [
    CommonModule,
    PersonnelRoutingModule
  ]
})
export class PersonnelModule { }
