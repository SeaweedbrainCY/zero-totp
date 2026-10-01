import { Component, inject, input, signal } from '@angular/core';
import { TranslateService } from '@ngx-translate/core';
import { TOTPEntry } from '../../models/totp-entry';
import { ToastService } from '../../Services/Toast/toast.service';

@Component({
  selector: 'app-vault-view',
  imports: [],
  templateUrl: './vault-view.component.html',
  styleUrl: './vault-view.component.css',
})
export class VaultViewComponent {
  private toast = inject(ToastService);
  private translate = inject(TranslateService);

  // Parent's inputs
  vault = input.required<Map<string, TOTPEntry>>();
  isVaultReadOnly = input(false)


  // tags signals
  vaultTagsList =  signal<string[]>([]);
  selectedTags = signal<string[]>([]);

  // Search bar
  searchBarValue = signal("")


  selectTag(tag: string) {
    if (this.selectedTags().includes(tag)) {
      this.selectedTags.update(tags => tags.filter(e => e !== tag));
    } else {
      this.selectedTags.update(tags => [...tags, tag])
    }
  }

  // Evaluates if a code should be displayed. The logic check the filtering tags and search items
  // It is important to keep the dynamic part selectedTagsList and searchBarValue as args because its the update of those values, catched in the HTML component that will re-trigger the function evaluation
  shouldDisplayCode(totpEntry: TOTPEntry, selectedTagsList: string[], searchBarValue: string): boolean {
    if (selectedTagsList.length == 0 && searchBarValue == "") {
      return true
    }

    if (selectedTagsList.length > 0) {
      let hasOneGoodTag = false
      for (let tag of selectedTagsList) {
        if (totpEntry.tags.includes(tag)) {
          hasOneGoodTag = true;
          break;
        }
      }
      if (!hasOneGoodTag) {
        return false
      }
    }

    if (searchBarValue != "") {
      let filter = searchBarValue.replace(/[^a-zA-Z0-9-_]/g, '').toLowerCase()
      if (filter.length > 50) {
        // Avoid slowing down the browser. Ne search with more than 50 char
        filter = filter.substring(0, 50)
      }
      if (!totpEntry.name.includes(filter) && !totpEntry.uri.includes(filter)) {
        return false
      }
    }
    return true
  }


  copy() {
    this.toast.success(this.translate.instant("copied"));
  }



}
