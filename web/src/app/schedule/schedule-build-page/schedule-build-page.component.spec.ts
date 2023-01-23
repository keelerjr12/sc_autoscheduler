import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ScheduleBuildPageComponent } from './schedule-build-page.component';

describe('ScheduleBuildPageComponent', () => {
  let component: ScheduleBuildPageComponent;
  let fixture: ComponentFixture<ScheduleBuildPageComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ScheduleBuildPageComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ScheduleBuildPageComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
