import { Component } from '@angular/core';
import { faChevronDown, faChevronUp } from '@fortawesome/free-solid-svg-icons';

@Component({
    selector: 'app-open-source-library',
    templateUrl: './open-source-library.component.html',
    styleUrls: ['./open-source-library.component.css'],
    standalone: false
})
export class OpenSourceLibraryComponent {
  MITlicenseExpanded=false;
  ApachelicenseExpanded=false;
  BSD3licenseExpanded=false;
  BSD2licenseExpanded=false;
  GPLlicenseExpanded=false;
  faChevronDown=faChevronDown;
  faChevronUp=faChevronUp;
  openSourceLibraries = [
    {
      name: "Angular",
      url: "https://angular.io/",
      description: "Angular is a platform for building mobile and desktop web applications.",
      license: "MIT license",
      copyright: "Copyright (c) 2010-2023 Google LLC.",
      licenseUrl: "https://angular.io/license"
    },
   {
    name:"@types/url-parse",
    url:"https://github.com/DefinitelyTyped/DefinitelyTyped/",
    description:"TypeScript URL parsing library.",
    license:"MIT license",
    copyright:"",
    licenseUrl:"https://github.com/DefinitelyTyped/DefinitelyTyped/blob/master/LICENSE"
   },
   {
    name:"@zxing/ngx-scanner",
    url:"https://github.com/zxing-js/ngx-scanner",
    description:"Angular QRcode Scanner.",
    license:"MIT license",
    copyright: "Copyright (c) 2018 zxing-web project",
    licenseUrl:"https://github.com/zxing-js/ngx-scanner/blob/master/LICENSE"
   },
   {
    name:"@ng-idle/core",
    url:"https://github.com/moribvndvs/ng2-idle#readme",
    description:"A module for responding to idle users in Angular applications.",
    license:"Apache-2.0 license",
    licenseUrl:""
   },
    {
      name:"Buffer",
      url:"https://github.com/feross/buffer",
      description: "The buffer module from node.js, for the browser.",
      license:"MIT license",
      copyright:"Copyright (c) Feross Aboukhadijeh, and other contributors.",
      licenseUrl:"https://github.com/feross/buffer/blob/master/LICENSE"
    },
    {
      name:"bulma-modal-fx",
      url:"https://github.com/postare/bulma-modal-fx",
      description:"Modal effects for Bulma.io.",
      license:"MIT license",
      licenseUrl:"https://github.com/postare/bulma-modal-fx/blob/master/LICENSE",
      copyright:"Copyright (c) 2018 Posta.re",
    },
    {
      name:"ngx-toastr",
      url:"https://github.com/scttcper/ngx-toastr",
      description:"🍞 Angular Toastr",
      license:"MIT license",
      licenseUrl:"https://github.com/scttcper/ngx-toastr?tab=MIT-1-ov-file#readme",
      copyright:"Copyright (c) Scott Cooper <scttcper@gmail.com"
    },
    {
      name:"bulma",
      url:"https://bulma.io",
      description:"Bulma is a free, open source CSS framework based on Flexbox and used by more than 200,000 developers.",
      license:"MIT license",
      licenseUrl:"https://github.com/jgthms/bulma/blob/master/LICENSE",
      copyright:"Copyright (c) 2023 Jeremy Thomas",
    },
    {
      name:"totp-generator",
      url:"https://github.com/bellstrand/totp-generator",
      description:"A TOTP generator for Node.js and the browser.",
      license:"MIT license",
      licenseUrl:"https://github.com/bellstrand/totp-generator/blob/master/LICENSE",
      copyright:"Copyright (c) 2016 Magnus Bellstrand",
    },
    {
      name:"bcrypt",
      url:"https://github.com/pyca/bcrypt",
      description:"Python implementation of BCrypt hashing algorithm.",
      license:"Apache-2.0 license",
      licenseUrl:"https://github.com/pyca/bcrypt/blob/main/LICENSE",
      copyright:"",
    },
    {
      name:"connexion",
      url:"https://github.com/spec-first/connexion",
      description:"Swagger/OpenAPI First framework for Python on top of Flask with automatic endpoint validation & OAuth2 support.",
      license:"Apache-2.0 license",
      licenseUrl:"https://github.com/spec-first/connexion/blob/main/LICENSE",
      copyright:"",
    },
    {
      name:"coveragepy",
      url:"https://github.com/nedbat/coveragepy",
      description:"Code coverage measurement for Python.",
      license:"Apache-2.0 license",
      licenseUrl:"https://github.com/nedbat/coveragepy/blob/master/LICENSE.txt",
      copyright:"",
    },
    {
      name:"Flask",
      url:"https://github.com/pallets/flask",
      description:"Flask is a lightweight WSGI web application framework. It is designed to make getting started quick and easy, with the ability to scale up to complex applications.",
      license:"BSD-3-Clause license",
      licenseUrl:"https://github.com/pallets/flask/blob/main/LICENSE.rst",
      copyright:"",
    },
    {
      name:"google-api-python-client",
      url:"https://github.com/googleapis/google-api-python-client",
      description:"Google API Client Library for Python.",
      license:"Apache-2.0 license",
      licenseUrl:"https://github.com/googleapis/google-api-python-client/blob/main/LICENSE",
      copyright:"",
    },
    {
      name:"gunicorn",
      url:"https://github.com/benoitc/gunicorn",
      description: "gunicorn  is a WSGI and ASGI HTTP Server for UNIX, fast clients and sleepy applications.",
      license:"MIT license",
      licenseUrl:"https://github.com/benoitc/gunicorn/blob/master/LICENSE",
      copyright:"2009-2023 (c) Benoît Chesneau <benoitc@gunicorn.org>",
    },
    {
      name:"pycryptodome",
      url:"https://github.com/Legrandin/pycryptodome/",
      description:"Cryptographic library for Python.",
      license:"BSD-2-Clause license",
      licenseUrl:"https://github.com/Legrandin/pycryptodome/blob/master/LICENSE.rst",
      copyright:"",
    },
    {
      name:"mysqlclient",
      url:"https://github.com/PyMySQL/mysqlclient",
      description:"MySQL database connector for Python.",
      license:"GPL-2.0 license",
      licenseUrl:"https://github.com/PyMySQL/mysqlclient/blob/main/LICENSE",
      copyright:"",
    },
    {
      name:"PyJWT",
      url:"https://github.com/jpadilla/pyjwt",
      description:"JSON Web Token implementation in Python.",
      license:"MIT license",
      licenseUrl:"https://github.com/jpadilla/pyjwt/blob/master/LICENSE",
      copyright:"Copyright (c) 2015-2022 José Padilla",
    },
    {
      name:"pytest",
      url:"https://github.com/pytest-dev/pytest",
      description:"The pytest framework makes it easy to write small tests, yet scales to support complex functional testing.",
      license:"MIT license",
      licenseUrl:"https://github.com/pytest-dev/pytest/blob/main/LICENSE",
      copyright:"Copyright (c) 2004 Holger Krekel and others",
    },
    {
      name:"requests",
      url:"https://github.com/psf/requests",
      description:"Requests is an elegant and simple HTTP library for Python, built for human beings.",
      license:"Apache-2.0 license",
      licenseUrl:"https://github.com/psf/requests/blob/main/LICENSE",
      copyright:"",
    },
    {
      name:"SQLAlchemy",
      url:"https://github.com/sqlalchemy/sqlalchemy",
      description:"SQLAlchemy is the Python SQL toolkit and Object Relational Mapper that gives application developers the full power and flexibility of SQL.",
      license:"MIT license",
      licenseUrl:"https://github.com/sqlalchemy/sqlalchemy/blob/main/LICENSE",
      copyright:"Copyright 2005-2023 SQLAlchemy authors and contributors."
    },
    {
      name:"Werkzeug",
      url:"https://github.com/pallets/werkzeug/",
      description:"The comprehensive WSGI web application library.",
      license:"BSD-3-Clause license",
      licenseUrl:"https://github.com/pallets/werkzeug/blob/main/LICENSE.rst",
      copyright:"",
    }
  ];

  getMITlicense() {
    return this.openSourceLibraries.filter((item) => item.license == 'MIT license');
  }

  getApacheLicense() {
    return this.openSourceLibraries.filter((item) => item.license == 'Apache-2.0 license');
  }

  getBSD3License() {
    return this.openSourceLibraries.filter((item) => item.license == 'BSD-3-Clause license');
  }

  getBSD2License() {
    return this.openSourceLibraries.filter((item) => item.license == 'BSD-2-Clause license');
  }

  getGPL2License() {
    return this.openSourceLibraries.filter((item) => item.license == 'GPL-2.0 license');
  }
}
