import { Component } from '@angular/core';
import { faCirclePlus, faTruckMedical } from '@fortawesome/free-solid-svg-icons';
import { environment } from 'src/environments/environment';

@Component({
  selector: 'app-changelog',
  templateUrl: './changelog.component.html',
  styleUrls: ['./changelog.component.css']
})
export class ChangelogComponent {
  faCirclePlus = faCirclePlus;
  faTruckMedical = faTruckMedical;
  imageHash = environment.imageHash;

  changelogs = [
    {
      date: "01/12/2023",
      version: "b1.6",
      added: [
        "We added a new page to list and be transparent about the open-source libraries we use in Zero-TOTP. You can find this page in the footer."
      ],
      fixed:[]
    },
    {
      date: "20/11/2023",
      version: "b1.5",
      added: [
        "You can now completely delete your account, including all your data. You can delete your account in your account settings.",
       "We improved the security surrounding admins.",
        "Rescue Zero-TOTP is now available for all. This version includes the integration of rescue.zero-totp.com in case of problems."
      ],
      fixed:["We patched CVE-2023-49083 (critical) from the python 'cryptography' library."]
    },
    {
      date: "20/11/2023",
      version: "b1.4",
      added: [
      ],
      fixed:[
        "A bug when opening the vault for the first time, the google drive status was stuck in loading status.",
        "We improve the database initialization on app startup.",
        "We improve the vault import via a zero-totp backup file.",
        "We improve the way we display time, to be more accurate according to your timezone. We fixed a bug when backuping your vault, the last backup up was not displayed.",
        "We fixed a bug in the adding a secret section causing the save button to be disabled even if the form was valid.",
        "We fixed the 'Reload my vault' button in your storage options which wasn't working properly.",
        "We improve the userflow when updating your passphrase, showing you multiple options if you have backups in your google drive."]
    },
    {
      date: "19/11/2023",
      version: "b1.3",
      added: [
        "We migrated the API from an WSGI server to a ASGI server to improve the performance of the application. As for now, the API is 20% faster and can handle more requests at the same time.",
        "We upgraded Zero-TOTP's API to Flask 3.0, connexion 3.0 to improve the performance and security of the application. This is an important upgrade in the maintainability and futur development of the application."
      ],
      fixed:[
        "We upgraded all the dependencies of the API to keep Zero-TOTP secure. In particular, the API is now protected against CVE-2023-46136 (moderate), CVE-2023-45803 (moderate) and CVE-2023-43804 (moderate)."]
    },
    {
      date: "18/11/2023 ",
      version: "b1.2",
      added: [
        "A full new section to manage your preferences and settings. The advances settings are now in this dedicated page.",
        "We added a whole new feature to Zero-TOTP : the favicon preview. You can now see the favicon of the website you are adding to your vault. It is easier to identify the website you are adding to your vault.",
        "You can enable or disable the favicon preview for each website in their settings. If you want to define a global setting for all your websites, you can do it in the preferences page. You can enable the favicon preview for all your websites or disable it for all your websites. This setting overriddes the website settings."
      ],
      fixed:[
       ]
    },
    {
      date: "09/11/2023 ",
      version: "b1.0",
      added: [
        "Your can now enable the automatic backup of your encrypted vault right into your Google Drive account in few clicks. After each modification to your vault an encrypted backup is automatically triggered and saved in your Google Drive account. You now have the control over your backups and stores them in a safe place. All backups are always encrypted with your passphrase and no one can open them without it. Even if someone has access to your Google Drive account.",
        "A full integration with Google Drive API to allow you to backup your vault in your Google Drive account through an OAuth2 authentication.",
        "A full control of your integration settings, directly from the vault page. You can enable or revoke the google drive backup, manage errors, or see the last backup date.",
        "We have designed a entire secure flow through the application to easily connect your google drive account within few clicks.",
        "We added an important new security layer to safely store your google drive access.",
        "We added a cleaning routine to manage for you the backup files in your google drive account.",
        "This new version includes a version control and integrity of your backups to always keep your backups up to date.",
        "We added new settings in your account page to see the whole backup retention policy. You will be able to manage it in futur releases.",
        "You can verify at any moment your google drive integration status right in your vault page.",
        "We updated the privacy policy to be more clearer about the google drive integration.",
        "This version brings a whole new dimension to Zero-TOTP and include a very important security layer for your vault to keep your data safe."
      ],
      fixed:[
       ]
    },
    {
      date: "31/10/2023",
      version: "b0.49",
      added: [
       
      ],
      fixed:[
        "We've made some improvement to the published docker images to be more secure and stable.",
        "You can now retrieve a specific version in dockerhub with its appropriate tag.",
        "We deleted a lot of debug logs to improve the application performance and avoid any security leak in your logs."
       ]
    },
    {
      date: "27/10/2023",
      version: "b0.48",
      added: [
        "A very strong and strict Content-Security-Policy (CSP) to add an extra layer of security to Zero-TOTP, particularly against XSS attacks, clickjacking, XSF, etc.",
        "This strict new policy is applied to all pages of Zero-TOTP and may cause some visual perturbations on some browsers. If you encounter any issue, please contact us. We will deeply test the application and apply some fixes if needed in futur releases.",
        "We upgraded our base image for the Zero-TOTP API's to improve the security of the application.",
      ],
      fixed:[
       ]
    },
    {
      date: "24/10/2023",
      version: "b0.47",
      added: [
       
      ],
      fixed:[
        'We added a better verification of your inputs to improve the application security at a very global scale.',
        'We added a strong sanitizing of all inputs to avoid any security issue.',
        'The "confirm your passphrase is strong" pop-up is now showed only once, even if your signup form has an error.You can now re-submit a signup without having to fill the pop-up again.',
        'As for now, if your session is expired or if you don\'t have internet anymore, the frontend can adapt to display more accurate error message and send you to the login page if your 1h session is ended.',
        'The "Create my vault" button on the home page is now "Open my vault" and leads to the login page instead. It is more convenient for most of users.',

       ]
    },
    {
      date: "23/10/2023",
      version: "b0.46",
      added: [
       "A very basic admin dashboard to visualize users (for admins only). Admins will never be able to modify view or modify users' data.",
       "We added a new login flow to secure the admin authentification."
      ],
      fixed:[
        "We've made some upgrades to always use the most stable packages.",
       ]
    },
    {
      date: "18/10/2023",
      version: "b0.45",
      added: [
      ],
      fixed:[
        "We've made some update of our dependencies to keep Zero-TOTP secure.",
       ]
    },
    {
      date: "16/10/2023",
      version: "b0.44",
      added: [
        "This changelog page.",
      ],
      fixed:[
       
       ]
    },
    {
      date: "16/10/2023",
      version: "b0.43",
      added: [
        "Zero-TOTP servers are now hosted in France and in Canada to improve the data redundancy.",
      ],
      fixed:[
       
       ]
    },
  ]

}
