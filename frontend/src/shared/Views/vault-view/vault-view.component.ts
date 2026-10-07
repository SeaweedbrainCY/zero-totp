import { Component, inject, input, signal, effect, OnInit, OnDestroy } from '@angular/core';
import { TranslateService, TranslatePipe } from '@ngx-translate/core';
import { TOTPEntry } from '../../models/totp-entry';
import { ToastService } from '../../Services/Toast/toast.service';
import { TOTP } from "totp-generator"
import {  RouterLink } from '@angular/router';
import { NgClass } from '@angular/common';
import { domain_name_validator, getDomainFromURI } from 'src/shared/Utils/utils';
import { faCopy, faPen, faSquarePlus, faCircleNotch, faXmark, faMagnifyingGlass } from '@fortawesome/free-solid-svg-icons';
import { CdkCopyToClipboard } from '@angular/cdk/clipboard';
import { FaIconComponent } from '@fortawesome/angular-fontawesome';
import { FormsModule } from '@angular/forms';

// TODO: configure usage of isVaultReadOnly
// Integrate the difference behavior as it was (when vault refresh for ex.)

@Component({
  selector: 'app-vault-view',
  imports: [TranslatePipe, RouterLink, NgClass, CdkCopyToClipboard, FaIconComponent, FormsModule],
  templateUrl: './vault-view.component.html',
  styleUrl: './vault-view.component.css',
})
export class VaultViewComponent implements OnInit, OnDestroy {
  private toast = inject(ToastService);
  private translate = inject(TranslateService);

  // Parent's inputs
  vault = input.required<Map<string, TOTPEntry>>();
  isVaultReadOnly = input(false)
  isVaultLoading = input(false)
  userFaviconPolicy = input("")


  // tags signals
  vaultTagsList =  signal<string[]>([]);
  selectedTags = signal<string[]>([]);

  // Search bar
  searchBarValue = signal("")
  filter = "";

  // Vault signals
  totpCodesMap = signal<Map<string, string>>(new Map<string, string>())

  // TOTP generation UI
  totpValidityUIAnimationIntervalID = 0
  totpGenerationIntervalID: number = 0
  totpGenerationTimeoutID = 0
  totpValidityUIAnimationTimeoutID = 0
  progress_bar_percent = signal(0);

  // Add a new totp code modal
  isAddTOTPModalActive = signal(false)


  // icons
  faCopy = faCopy;
  faPen = faPen;
  faSquarePlus = faSquarePlus;
  faCircleNotch = faCircleNotch;
  faXmark = faXmark;
  faMagnifyingGlass = faMagnifyingGlass;


  constructor() {
    // generateCode() reads this.vault(), so this effect re-runs every time the parent passes a new vault
    // (e.g. once decryption is done), instead of waiting for the next 30s tick.
    effect(() => this.generateCode());
  }

  ngOnInit(): void {
    if (!this.isVaultReadOnly()) {
      document.getElementById("add-code-button")!.style.display = "flex";
      document.getElementById("add-code-button")!.onclick = () => { this.isAddTOTPModalActive.set(true); };
    }
    this.startDisplayingCode()
  }

  ngOnDestroy() {
    clearTimeout(this.totpGenerationTimeoutID)
    clearInterval(this.totpGenerationIntervalID)

    clearTimeout(this.totpValidityUIAnimationTimeoutID)
    clearInterval(this.totpValidityUIAnimationIntervalID)

    // Hide the add button
    document.getElementById("add-code-button")!.style.display = "none";
  }


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

  generateCode() {
    let newTOTPCodesMap = new Map<string, string>()
    for (let uuid of this.vault().keys()) {
      const secret = this.vault().get(uuid)!.secret;
      try {
        let code = TOTP.generate(secret).otp
        newTOTPCodesMap.set(uuid, code)
      } catch (e) {
        console.log(e);
        newTOTPCodesMap.set(uuid, "Error")
      }
    }
    this.totpCodesMap.set(newTOTPCodesMap)
  }

  // Return epoch time a totp codes needs to be generated
  getNextTOTPGenerationEpochTime(): number {
    return (Math.floor(Date.now() / 30_000) + 1) * 30_000
  }

  startTOTPGenerationInterval() {
    this.generateCode()
    // TOTP generation interval. Every 30 s
    let msUntilNextGeneration = this.getNextTOTPGenerationEpochTime() - Date.now()
    this.totpGenerationTimeoutID = window.setTimeout(() => {
      this.generateCode()
      this.totpGenerationIntervalID = window.setInterval(() => {
        this.generateCode()
      }, 30_000)
    }, msUntilNextGeneration)
  }

  updateTOTPValidationUI() {
    let msUntilNextGeneration = this.getNextTOTPGenerationEpochTime() - Date.now()
    this.progress_bar_percent.set(msUntilNextGeneration / 300)
  }

  startTOTPValidityUIAnimation() {
    this.updateTOTPValidationUI()
    // Update TOTP validity animation. Every 1s

    // TOTP codes generate on exact second, like 14:30:00,000. So validity animation should update every plain second, ie ms=000
    const now = Date.now()
    let msUntilPlainSecond = (Math.floor(now / 1000) + 1) * 1000 - now
    this.totpValidityUIAnimationTimeoutID = window.setTimeout(() => {
      this.updateTOTPValidationUI()
      this.totpValidityUIAnimationIntervalID = window.setInterval(() => {
        this.updateTOTPValidationUI()
      }, 1000)
    }, msUntilPlainSecond)
  }


  // Display code in the UI. Will call all the underlying display and compute func
  startDisplayingCode() {
    if (this.totpValidityUIAnimationIntervalID == 0 && this.totpValidityUIAnimationTimeoutID == 0) {
      this.startTOTPValidityUIAnimation()
    }
    if (this.totpGenerationIntervalID == 0 && this.totpGenerationTimeoutID == 0) {
      this.startTOTPGenerationInterval()
    }
  }

  searchBarValueChanged() {
    this.searchBarValue.set(this.filter)
  }

  get_favicon_url(unsafe_uri: string | undefined): string {
    const unsafe_domain = unsafe_uri ? getDomainFromURI(unsafe_uri) : "";
    const domain = domain_name_validator(unsafe_domain) ? unsafe_domain : "unknown";
    const url = new URL(`/ip3/${domain}.ico`, "https://icons.duckduckgo.com");
    return url.toString();
  }


  getColorFromTOTPColorType(colorType: string): string {
    switch (colorType) {
      case "success": return "#63A375"
      case "danger": return "#FE6847"
      case "warning": return "#FFCF56"
      default: return "#5AA9E6"
    }
  }



}
