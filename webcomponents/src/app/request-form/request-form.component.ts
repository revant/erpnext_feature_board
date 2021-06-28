import { Component } from '@angular/core';
import { MatDialogRef } from '@angular/material/dialog';

@Component({
  selector: 'app-request-form',
  templateUrl: './request-form.component.html',
  styleUrls: ['./request-form.component.css'],
})
export class RequestFormComponent {
  options = ['Add Testing User', 'Build', 'Upgrade', 'Delete'];

  selected: string = '';

  constructor(public dialogRef: MatDialogRef<any>) {}

  request() {
    this.dialogRef.close({ data: this.selected });
  }
}
