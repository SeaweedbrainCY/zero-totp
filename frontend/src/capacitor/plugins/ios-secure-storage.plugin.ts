import { registerPlugin } from '@capacitor/core';

export interface iOSSecureStoragePlugin {
    /** Store a string value under the given key. Overwrites if the key already exists. */
    set(options: { key: string; value: string }): Promise<void>;

    /** Retrieve a value by key. Resolves with `null` if the key does not exist. */
    get(options: { key: string }): Promise<{ value: string | null }>;

    /** Delete a key. No-op if the key does not exist. */
    remove(options: { key: string }): Promise<void>;
}

export const iOSSecureStorage = registerPlugin<iOSSecureStoragePlugin>('iOSSecureStorage');