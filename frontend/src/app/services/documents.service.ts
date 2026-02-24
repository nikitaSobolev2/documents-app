import { HttpClient, HttpParams } from '@angular/common/http';
import {
  DocumentCreateRequest,
  DocumentStatus,
  DocumentCreateResponse,
  DocumentDetailResponse,
  DocumentListResponse,
  DocumentUpdateStatusResponse,
} from '../models/documents';
import { inject, Injectable } from '@angular/core';
import { environment } from '../environments/environment';
import { Observable } from 'rxjs';

interface IDocumentsService {
  createDocument(document: DocumentCreateRequest): Observable<DocumentCreateResponse>;
  getDocument(documentId: number): Observable<DocumentDetailResponse>;
  getDocumentList(limit: number, offset: number): Observable<DocumentListResponse>;
  updateDocumentStatus(
    documentId: number,
    status: DocumentStatus,
  ): Observable<DocumentUpdateStatusResponse>;
}

@Injectable({
  providedIn: 'root',
})
export class DocumentsService implements IDocumentsService {
  private readonly baseUrl = environment.backendUrl;
  private readonly http = inject(HttpClient);

  getDocument(documentId: number): Observable<DocumentDetailResponse> {
    return this.http.get<DocumentDetailResponse>(`${this.baseUrl}/v1/documents/${documentId}`);
  }

  getDocumentList(limit: number, offset: number): Observable<DocumentListResponse> {
    const params = new HttpParams().set('limit', limit).set('offset', offset);

    return this.http.get<DocumentListResponse>(`${this.baseUrl}/v1/documents/`, { params });
  }

  createDocument(document: DocumentCreateRequest): Observable<DocumentCreateResponse> {
    return this.http.post<DocumentCreateResponse>(`${this.baseUrl}/v1/documents/`, document);
  }

  updateDocumentStatus(
    documentId: number,
    status: DocumentStatus,
  ): Observable<DocumentUpdateStatusResponse> {
    return this.http.patch<DocumentUpdateStatusResponse>(
      `${this.baseUrl}/v1/documents/${documentId}/status/${status}`,
      null,
    );
  }
}
