import { registerPlugin } from '@capacitor/core';

export interface iOSSecureStoragePlugin {
    /** Store a string value under the given key. Overwrites if the key already exists. */
    set(options: { key: string; value: string }): Promise<void>;

    /** Retrieve a value by key. Resolves with `null` if the key does not exist. */
    get(options: { key: string }): Promise<{ value: string | null }>;

    /** Delete a key. No-op if the key does not exist. */
    remove(options: { key: string }): Promise<void>;

    /** Store a value protected by Face ID / Touch ID / device passcode. */
    setProtected(options: { key: string; value: string }): Promise<void>;

    /**
     * Retrieve a biometric-protected value.
     * Triggers the system authentication sheet with the given prompt.
     * Rejects with code `USER_CANCELLED` if the user dismisses the sheet,
     * or `AUTH_FAILED` if biometry is exhausted / locked out.
     * Resolves with `null` if the key does not exist (no auth is attempted).
     */
    getProtected(options: { key: string; prompt: string | undefined }): Promise<{ value: string | null }>;
}

export const iOSSecureStorage = registerPlugin<iOSSecureStoragePlugin>('iOSSecureStorage');