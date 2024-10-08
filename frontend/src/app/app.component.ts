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
  constructor(private renderer: Renderer2, @Inject(DOCUMENT) private document: Document) { }

  // This function should be called after the external library has added the script to the head section
  addNonceToDynamicallyAddedScripts() {
    const scripts = this.document.querySelectorAll('script');
    
    scripts.forEach(script => {
      // Check if the script is dynamically added by the external library
      if (!script.hasAttribute('nonce')) {
        // Add the nonce attribute
        this.renderer.setAttribute(script, 'nonce', 'random-nonce-placeholder'); // Replace with your actual nonce value
      }
    });
  }


  ngOnInit(): void {
  }

}



// Inject the document object

