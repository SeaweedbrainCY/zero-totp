import { Component, signal, OnInit, inject } from '@angular/core';
import { TranslatePipe, TranslateService } from '@ngx-translate/core';
import { faLanguage } from '@fortawesome/free-solid-svg-icons';
import { NgClass } from '@angular/common';
import { FaIconComponent } from '@fortawesome/angular-fontawesome';

type Lang = {
    code: string,
    name:string
}


@Component({
  selector: 'app-navbar-lang-selector',
  imports: [
    TranslatePipe,
    NgClass,
    FaIconComponent
  ],
  templateUrl: './navbar-lang-selector.component.html',
  styleUrl: './navbar-lang-selector.component.css',
})



export class NavbarLangSelectorComponent implements OnInit {
  // DI
  translate = inject(TranslateService)

  // signals
  isLangDropdownExpanded = signal(false)
  availableLangs = signal<Lang[]>([])

  //icons
  faLanguage = faLanguage


  ngOnInit(): void {
     const langs = this.translate.getLangs()
       .map(code => ({ code, name: this.getLangName(code) }))
       .sort((a, b) => a.name.localeCompare(b.name))
     this.availableLangs.set(langs)
   }

   // Name of the language in its own language (e.g. "Français", "English")
   private getLangName(code: string): string {
     const baseLang = code.split('-')[0]
     try {
       const name = new Intl.DisplayNames([baseLang], { type: 'language' }).of(baseLang) ?? code
       return name.charAt(0).toLocaleUpperCase(baseLang) + name.slice(1)
     } catch {
       return code
     }
   }


  changeLanguage(language: string) {
    this.isLangDropdownExpanded.set(false);
    if (language == 'fr-fr') {
      localStorage.setItem('language', 'fr-fr');
      this.translate.use('fr-fr');
    } else { // 'en-uk' + default
      localStorage.setItem('language', 'en-uk');
      this.translate.use('en-uk');
    }
  }
}
