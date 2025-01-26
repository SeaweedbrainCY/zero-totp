import { Component, OnInit } from '@angular/core';
import { environment } from 'src/environments/environment';
import { Renderer2, Inject } from '@angular/core';
import { DOCUMENT } from '@angular/common';


@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit{
  title = 'frontend';
  constructor(private renderer: Renderer2, @Inject(DOCUMENT) private document: Document) { 
    const theme = localStorage.getItem('theme');
    if (theme == 'dark') {
      this.renderer.setAttribute(document.documentElement, 'data-theme', 'dark');
    } else {
      this.renderer.setAttribute(document.documentElement, 'data-theme', 'light');
    }
  }

  

  ngOnInit(): void {
  }

}



// Inject the document object

