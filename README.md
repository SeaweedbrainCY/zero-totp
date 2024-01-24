# Zero-TOTP
<p align="center">
    <img src="https://img.shields.io/uptimerobot/status/m794827592-25c510a0c14f34a3812711a9%20?label=zero-totp.com&link=zero-totp.com"/>
    <img src="https://img.shields.io/uptimerobot/status/m794828362-be618abc0d9ba7230401e6af?label=api.zero-totp.com&link=zero-totp.com"/>
    <br>
    <img src="https://github.com/SeaweedbrainCY/zero-totp/actions/workflows/main.yml/badge.svg?branch="/>
     <a href="https://github.com/SeaweedbrainCY/zero-totp/actions/workflows/test.yml"><img src="https://github.com/SeaweedbrainCY/zero-totp/actions/workflows/test.yml/badge.svg" alt="Test and Coverage"/></a>
    <a href='https://coveralls.io/github/SeaweedbrainCY/zero-totp'><img src='https://coveralls.io/repos/github/SeaweedbrainCY/zero-totp/badge.svg' alt='Coverage Status' /></a>
    <img src="https://img.shields.io/github/license/seaweedbraincy/zero-totp"/>
</p>

<img src="https://github.com/SeaweedbrainCY/zero-totp/blob/main/frontend/src/assets/logo_zero_totp_dark.png?raw=true"/>

**Contributors :**

![GitHub Contributors Image](https://contrib.rocks/image?repo=seaweedbraincy/zero-totp)

## The project 
Zero-totp is a TOTP client project available as a **web app**, an **iOS app** and a **CLI app**, where you can **safely store all your TOTP codes** and retrieve easly retrieve them anywhere, anytime.

It's a **100% open source project**, based on a **zero-knowledge encryption**, which means that nobody, even the hosting platform, can read your data, except you and yourself. 

You are the only one able to decrypt these information, thanks to your strong and secure `passphrase` ;) 

*Zero Knowledge Encryption (ZKE) refers to a robust security measure that ensures the utmost protection of your data. With ZKE, your information is encrypted locally on your device before being uploaded to the cloud, and only you hold the encryption keys, guaranteeing that no one, including the service provider, can access your data without your explicit permission. This empowers you with complete control over your sensitive information while enjoying the convenience and flexibility of cloud storage.*

## Project progress
*Updated 23 jan. 2024*
> [!TIP]
> As of today, all focus is on the web app (main and Rescue) and their self-hosted version. The iOS app and the CLI app are not in development for the moment.

| Platform | In development | In beta Test | Stable |
| --- | --- | --- | --- |
| [Rescue Zero-TOTP](https://rescue.zero-totp.com) | ✅ | ✅ | ✅ |
| [Zero-TOTP Web App](https://zero-totp.com) | ✅ | ✅ | ⏳ |
| Zero-TOTP web app self-host | ✅ | ⏳ | ⏳ |
| Rescue Zero-TOTP self-host | ✅ | ⏳ | ⏳ |
| Zero-TOTP iOS App | ⏳ | ⏳ | ⏳ |
| Zero-TOTP CLI App | ⏳ | ⏳ | ⏳ |

## Secure and reliable

To be sure that you always have access to your TOTP codes, we use the benefits of the zero-knowledge encryption to offer you a complete control of your data and its replication : 
1. You can store your mega-secure encrypted vault **3 different locations**   
    - The database of zero-totp.com **(default)**
    - Into google drive **(recommended and auto-sync)**
    - Into your machine
2. You have **5 different and independent** platform able to open your vault
    - zero-totp.com (for everyday usage)
    - The iOS application (for your mobile usage)
    - The CLI application (for most geek of us)
    - rescue.zero-totp.com (a simple, minimal and ULTRA stable frontend, hosted on github pages where you can upload your vault and decrypt it)
    - On your own machine, thanks to the zero-totp docker image

In summary : Your data is safe, even if your vault leak. Your data is available even if zero-totp.com is unreachable. 

## Contribution

All contributions are welcome ! Feel free to open a merge request 

## Licence 

The code is under GPL-3.0 Licence

Images and icons are free of use, but please, don't use them for commercial purpose.

Zero-TOTP is a project of Nathan Stchepinsky © 2023. All rights reserved.
