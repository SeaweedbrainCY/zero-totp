import Foundation
import Security
import LocalAuthentication

// MARK: - Errors

enum KeychainError: Error, LocalizedError {
    case notFound
    case encodingFailed
    case decodingFailed
    case accessControlFailed
    case operationFailed(OSStatus)

    var errorDescription: String? {
        switch self {
        case .notFound:
            return "Item not found in keychain"
        case .encodingFailed:
            return "Failed to encode value as UTF-8"
        case .decodingFailed:
            return "Failed to decode keychain data as UTF-8"
        case .accessControlFailed:
            return "Failed to create access control object"
        case .operationFailed(let status):
            return "Keychain operation failed (OSStatus \(status))"
        }
    }
}

// MARK: - Implementation

@objc public class SecureStorage: NSObject {

    private let service: String

    @objc public init(service: String) {
        self.service = service
        super.init()
    }

    // Upsert: update if exists, add otherwise.
    func set(key: String, value: String) throws {
        guard let data = value.data(using: .utf8) else {
            throw KeychainError.encodingFailed
        }

        let search: [CFString: Any] = [
            kSecClass:       kSecClassGenericPassword,
            kSecAttrService: service,
            kSecAttrAccount: key
        ]

        var status = SecItemUpdate(search as CFDictionary, [kSecValueData: data] as CFDictionary)

        if status == errSecItemNotFound {
            let add: [CFString: Any] = [
                kSecClass:          kSecClassGenericPassword,
                kSecAttrService:    service,
                kSecAttrAccount:    key,
                kSecValueData:      data,
                kSecAttrAccessible: kSecAttrAccessibleWhenUnlocked
            ]
            status = SecItemAdd(add as CFDictionary, nil)
        }

        guard status == errSecSuccess else {
            throw KeychainError.operationFailed(status)
        }
    }

    func get(key: String) throws -> String {
        let query: [CFString: Any] = [
            kSecClass:       kSecClassGenericPassword,
            kSecAttrService: service,
            kSecAttrAccount: key,
            kSecReturnData:  true,
            kSecMatchLimit:  kSecMatchLimitOne
        ]

        var result: AnyObject?
        let status = SecItemCopyMatching(query as CFDictionary, &result)

        switch status {
        case errSecSuccess:
            guard let data = result as? Data, let value = String(data: data, encoding: .utf8) else {
                throw KeychainError.decodingFailed
            }
            return value
        case errSecItemNotFound:
            throw KeychainError.notFound
        default:
            throw KeychainError.operationFailed(status)
        }
    }

    func remove(key: String) throws {
        let query: [CFString: Any] = [
            kSecClass:       kSecClassGenericPassword,
            kSecAttrService: service,
            kSecAttrAccount: key
        ]

        let status = SecItemDelete(query as CFDictionary)

        // Deleting a non-existent key is a no-op, not an error.
        guard status == errSecSuccess || status == errSecItemNotFound else {
            throw KeychainError.operationFailed(status)
        }
    }
    
    // Store a value protected by biometrics / device passcode.
    // Writing does NOT require authentication; only reading does.
    func setProtected(key: String, value: String) throws {
        guard let data = value.data(using: .utf8) else {
            throw KeychainError.encodingFailed
        }

        var cfError: Unmanaged<CFError>?
        guard let access = SecAccessControlCreateWithFlags(
            kCFAllocatorDefault,
            kSecAttrAccessibleWhenPasscodeSetThisDeviceOnly,  // requires passcode on device; not backed up
            .userPresence,                                     // Face ID / Touch ID / passcode fallback
            &cfError
        ) else {
            throw KeychainError.accessControlFailed
        }

        // Delete first: SecItemUpdate on a .userPresence item would itself
        // trigger an unwanted auth prompt, so delete + add is cleaner.
        let search: [CFString: Any] = [
            kSecClass:       kSecClassGenericPassword,
            kSecAttrService: service,
            kSecAttrAccount: key
        ]
        SecItemDelete(search as CFDictionary)  // intentionally ignore errSecItemNotFound

        let add: [CFString: Any] = [
            kSecClass:             kSecClassGenericPassword,
            kSecAttrService:       service,
            kSecAttrAccount:       key,
            kSecValueData:         data,
            kSecAttrAccessControl: access      
        ]

        let status = SecItemAdd(add as CFDictionary, nil)
        guard status == errSecSuccess else {
            throw KeychainError.operationFailed(status)
        }
    }

    // Retrieve a biometric-protected value.
    // `prompt` is shown in the system Face ID / Touch ID sheet.
    func getProtected(key: String, prompt: String) throws -> String {
        let context = LAContext()
        context.localizedReason = prompt   // shown in the biometric dialog

        let query: [CFString: Any] = [
            kSecClass:                    kSecClassGenericPassword,
            kSecAttrService:              service,
            kSecAttrAccount:              key,
            kSecReturnData:               true,
            kSecMatchLimit:               kSecMatchLimitOne,
            kSecUseAuthenticationContext: context   // system will call evaluatePolicy internally
        ]

        var result: AnyObject?
        let status = SecItemCopyMatching(query as CFDictionary, &result)

        switch status {
        case errSecSuccess:
            guard let data = result as? Data, let value = String(data: data, encoding: .utf8) else {
                throw KeychainError.decodingFailed
            }
            return value
        case errSecItemNotFound:
            throw KeychainError.notFound
        default:
            throw KeychainError.operationFailed(status)  // includes errSecAuthFailed if user cancels
        }
    }
}
