import { Injectable, signal, WritableSignal } from '@angular/core';

@Injectable({
  providedIn: 'root',
})

export class DisplayPreferencesService {
  public theme: WritableSignal<string> = signal("light")
}
