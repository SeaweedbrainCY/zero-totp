import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { UserService } from '../../../shared/Services/User/user.service';

// Redirects users whose email is not verified to the email verification page.
// Authentication itself is not enforced here: if the user can't be loaded, the
// navigation is allowed and the target component handles the session as before.
export const verifiedGuard: CanActivateFn = async () => {
  const userService = inject(UserService);
  const router = inject(Router);

  // On a page refresh, the guard runs before AppComponent has loaded the user
  if (userService.isEmailVerified() === null) {
    try {
      await userService.refresh_user_id();
    } catch {
      return true;
    }
  }

  if (userService.isEmailVerified() === false) {
    return router.createUrlTree(['/emailVerification']);
  }
  return true;
};
