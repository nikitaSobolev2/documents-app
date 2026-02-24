import { AppBaseResponse } from './system';

export enum DocumentStatus {
  DRAFT = 'draft',
  PUBLISHED = 'published',
  ARCHIVED = 'archived',
}

export enum DocumentProcessingTaskStatus {
  PENDING = 'pending',
  PROCESSING = 'processing',
  COMPLETED = 'completed',
  FAILED = 'failed',
}

export interface Document {
  id: number;
  title: string;
  content?: string | null;
  status: DocumentStatus;
}

export type DocumentList = Document[];

export interface DocumentCreateRequest {
  title: string;
  content?: string | null;
}

export interface DocumentCreateResponseData {
  celery_task_id: string;
  document_id: number;
  status: DocumentProcessingTaskStatus;
}

export type DocumentListResponse = AppBaseResponse<DocumentList>;
export type DocumentDetailResponse = AppBaseResponse<Document>;
export type DocumentCreateResponse = AppBaseResponse<DocumentCreateResponseData>;
export type DocumentUpdateStatusResponse = AppBaseResponse<Document>;
