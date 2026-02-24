import { Component, signal } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { DocumentsList } from './components/documents-list/documents-list';
import { DocumentUpload } from './components/document-upload/document-upload';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, DocumentUpload, DocumentsList],
  templateUrl: './app.html',
  styleUrl: './app.scss'
})
export class App {
  protected readonly title = signal('frontend');
}
