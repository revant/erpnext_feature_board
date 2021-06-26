import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ImprovementFormComponent } from './improvement-form.component';

describe('ImprovementFormComponent', () => {
  let component: ImprovementFormComponent;
  let fixture: ComponentFixture<ImprovementFormComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ImprovementFormComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ImprovementFormComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
