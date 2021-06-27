import { HttpClient } from '@angular/common/http';
import { Component, Input, OnInit } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';

@Component({
  selector: 'app-improvement-form',
  templateUrl: './improvement-form.component.html',
  styleUrls: ['./improvement-form.component.css'],
})
export class ImprovementFormComponent implements OnInit {
  @Input() docname: string = '';
  prNumber = '';
  prDescription = '';
  form = new FormGroup({
    repository: new FormControl(''),
    appName: new FormControl(''),
    deploymentStatus: new FormControl(''),
    title: new FormControl(''),
    description: new FormControl(''),
    prUrl: new FormControl(''),
    status: new FormControl(''),
    siteUrl: new FormControl(''),
  });

  constructor(private readonly http: HttpClient) {}

  ngOnInit() {
    this.http.get<any>(`/api/resource/Improvement/${this.docname}`).subscribe({
      next: (res) => {
        const { data } = res;
        this.prNumber = data.number;
        this.prDescription = data.description;
        this.form.controls.title.setValue(data.title);
        this.form.controls.repository.setValue(data.repository);
        this.form.controls.siteUrl.setValue(data.site_url);
        this.form.controls.prUrl.setValue(data.pull_request_url);
        this.form.disable();
      },
      error: (err) => {},
    });
  }
}
