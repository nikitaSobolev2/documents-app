export interface AppBaseResponse<T> {
  status: number;
  message: string;
  data?: T;
  errors?: string[];
  errorDetails?: any;
}
