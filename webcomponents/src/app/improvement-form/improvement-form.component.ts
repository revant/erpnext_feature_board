import { HttpClient } from '@angular/common/http';
import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';
import { MatDialog } from '@angular/material/dialog';
import { ListingService } from '../data-list/listing.service';
import { RequestFormComponent } from '../request-form/request-form.component';

@Component({
  selector: 'app-improvement-form',
  templateUrl: './improvement-form.component.html',
  styleUrls: ['./improvement-form.component.css'],
})
export class ImprovementFormComponent implements OnInit {
  @Input() docname: string = '';
  @Input() csrfToken: string = '';
  @Input() user: string = 'Guest';
  @Output() clickRow = new EventEmitter();
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
  filters: string[][] = [];
  fields = [
    'request_type',
    'request_status',
    'request_reject_reason',
    'test_user_name',
    'test_user_password',
    'name',
  ];
  linkName = false;

  constructor(
    private readonly http: HttpClient,
    private readonly dialog: MatDialog,
    private readonly listing: ListingService
  ) {}

  ngOnInit() {
    this.filters.push(
      ['user', '=', this.user],
      ['improvement', '=', this.docname]
    );
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

  requestToReview() {
    const dialogRef = this.dialog.open(RequestFormComponent, { width: '75%' });

    dialogRef.afterClosed().subscribe((data) => {
      if (data?.data && data?.data?.length > 0) {
        this.createRequest(data.data);
      }
    });
  }

  createRequest(requestType: string) {
    this.http
      .post(
        '/api/resource/Review%20Request',
        {
          improvement: this.docname,
          request_type: requestType,
        },
        { headers: { 'X-Frappe-CSRF-Token': this.csrfToken } }
      )
      .subscribe({
        next: (res) => {
          this.listing.refreshList('Improvement', this.filters, this.fields);
        },
        error: (err) => {},
      });
  }
}
