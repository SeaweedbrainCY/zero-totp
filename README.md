# Zero-TOTP

## The project 
Zero-totp is a TOTP client project available as a **web app**, an **iOS app** and a **CLI app**, where you can **safely store all your TOTP codes** and retrieve easly retrieve them anywhere, anytime.

It's a **100% open source project**, based on a **zero-knowledge encryption**, which means that nobody, even your the hosting platform, can read your data, except you and yourself. 

You are the one and only able to decrypt these information, thanks to your strong and secure `passphrase` ;) 

*Zero Knowledge Encryption (ZKE) refers to a robust security measure that ensures the utmost protection of your data. With ZKE, your information is encrypted locally on your device before being uploaded to the cloud, and only you hold the encryption keys, guaranteeing that no one, including the service provider, can access your data without your explicit permission. This empowers you with complete control over your sensitive information while enjoying the convenience and flexibility of cloud storage.*

## Secure and reliable

To be sure that you always have access to your TOTP codes, we use the benefits of the zero-knowledge encryption to offer you a complete control of your data and its replication : 
1. You can store your mega-secure encrypted vault **3 different locations**   
    - The database of zero-totp.fr **(default)**
    - Into google drive **(recommended and auto-sync)**
    - Into your machine
2. You have **5 different and independent** platform able to open your vault
    - zero-totp.fr (for everyday usage)
    - The iOS application (for your mobile usage)
    - The CLI application (for most geek of us)
    - rescue.zero-totp.fr (a simple, minimal and ULTRA stable frontend, hosted on github pages where you can upload your vault and decrypt it)
    - On your own machine, thanks to the zero-totp docker image

In summary : Your data is safe, even if your vault leak. Your data is safe even if zero-totp.com is unreachable. 

## Contribution

All contributions are welcome ! Feel free to open a merge request 

## Licence 

The code is under GPL-3.0 Licence

Images and icons are free of use, but please, don't use them for commercial purpose.

The Zero-TOTP projet is a project of Nathan Stchepinsky © 2023 copyright. All rights reserved.
