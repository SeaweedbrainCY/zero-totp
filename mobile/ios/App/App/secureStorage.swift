import Foundation
import Security

// MARK: - Errors

enum KeychainError: Error, LocalizedError {
    case notFound
    case encodingFailed
    case decodingFailed
    case operationFailed(OSStatus)

    var errorDescription: String? {
        switch self {
        case .notFound:
            return "Item not found in keychain"
        case .encodingFailed:
            return "Failed to encode value as UTF-8"
        case .decodingFailed:
            return "Failed to decode keychain data as UTF-8"
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
}