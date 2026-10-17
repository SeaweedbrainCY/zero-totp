import { Injectable, inject } from '@angular/core';
import { ToastrService } from 'ngx-toastr';

// Shared look & feel (position, close button, progress bar...) is configured once in provideToastr().
// Messages are rendered as text: keep enableHtml disabled, some toasts display server-provided messages.
@Injectable({ providedIn: 'root' })
export class ToastService {
  private toastr = inject(ToastrService);

  success(title: string, message = '') {
    this.toastr.success(message, title, { timeOut: 5000 });
  }

  error(title: string, message = '') {
    this.toastr.error(message, title, { timeOut: 30000 });
  }

  warning(title: string, message = '') {
    this.toastr.warning(message, title, { timeOut: 30000 });
  }

  clear() {
    this.toastr.clear();
  }
}
