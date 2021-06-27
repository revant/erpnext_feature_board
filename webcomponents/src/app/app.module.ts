import { DoBootstrap, Injector, NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { createCustomElement } from '@angular/elements';
import { ImprovementListComponent } from './improvement-list/improvement-list.component';
import { ImprovementFormComponent } from './improvement-form/improvement-form.component';
import { RequestListComponent } from './request-list/request-list.component';
import { RequestFormComponent } from './request-form/request-form.component';
import { DataListComponent } from './data-list/data-list.component';
import { ListFilterComponent } from './list-filter/list-filter.component';
import { MaterialModule } from './material.module';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';
import { FlexLayoutModule } from '@angular/flex-layout';

@NgModule({
  declarations: [
    DataListComponent,
    ListFilterComponent,
    ImprovementListComponent,
    ImprovementFormComponent,
    RequestListComponent,
    RequestFormComponent,
  ],
  imports: [
    BrowserModule,
    BrowserAnimationsModule,
    MaterialModule,
    FormsModule,
    ReactiveFormsModule,
    HttpClientModule,
    FlexLayoutModule,
  ],
  providers: [],
})
export class AppModule implements DoBootstrap {
  constructor(private injector: Injector) {}

  ngDoBootstrap() {
    const impList = createCustomElement(ImprovementListComponent, {
      injector: this.injector,
    });
    customElements.define('improvement-list', impList);

    const impForm = createCustomElement(ImprovementFormComponent, {
      injector: this.injector,
    });
    customElements.define('improvement-form', impForm);

    const reqList = createCustomElement(RequestListComponent, {
      injector: this.injector,
    });
    customElements.define('request-list', reqList);

    const reqForm = createCustomElement(RequestFormComponent, {
      injector: this.injector,
    });
    customElements.define('request-form', reqForm);
  }
}
