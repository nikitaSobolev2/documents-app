import { Component, inject } from '@angular/core';
import { DocumentsService } from '../../services/documents.service';
import { DocumentList } from '../../models/documents';
import { filter, interval, map, switchMap } from 'rxjs';
import { toSignal } from '@angular/core/rxjs-interop';

@Component({
  selector: 'app-documents-list',
  imports: [],
  templateUrl: './documents-list.html',
  styleUrl: './documents-list.scss',
})
export class DocumentsList {
  private readonly documentsService = inject(DocumentsService);

  public documents = toSignal(
    interval(3000).pipe(
      switchMap(() => this.documentsService.getDocumentList(10, 0)),
      filter(r => r.status === 200 && !!r.data),
      map(r => r.data as DocumentList)
    ),
    { initialValue: [] as DocumentList }
  );
}
