import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ImprovementListComponent } from './improvement-list.component';

describe('ImprovementListComponent', () => {
  let component: ImprovementListComponent;
  let fixture: ComponentFixture<ImprovementListComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ImprovementListComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ImprovementListComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
