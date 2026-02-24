import { Component, inject, signal } from '@angular/core';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { DocumentsService } from '../../services/documents.service';

@Component({
  selector: 'app-document-upload',
  imports: [ReactiveFormsModule],
  templateUrl: './document-upload.html',
  styleUrl: './document-upload.scss',
})
export class DocumentUpload {
  private readonly formBuilder = inject(FormBuilder);
  private readonly documentService = inject(DocumentsService);

  public error = signal<string | null>(null);
  public createdCeleryTaskId = signal<string | null>(null);

  public form: FormGroup = this.formBuilder.group({
    title: ['', [Validators.required, Validators.minLength(3)]],
    content: [null],
  });

  public createDocument(): void {
    if (this.form.invalid) {
      this.error.set('Form is invalid');
      return;
    }

    this.documentService.createDocument(this.form.value).subscribe({
      next: (response) => {
        if (response.status === 201) {
          this.createdCeleryTaskId.set(response.data?.celery_task_id ?? null);
        } else {
          this.error.set(response.message ?? 'Unknown error');
        }
      },
      error: (error) => {
        console.error(error);
        this.error.set(error.message);
      },
    });
  }
}
