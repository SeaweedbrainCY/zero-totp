import Foundation
import Capacitor

@objc(SecureStoragePlugin)
public class SecureStoragePlugin: CAPPlugin, CAPBridgedPlugin {

    public let identifier = "SecureStoragePlugin"
    public let jsName = "iOSSecureStorage"
    public let pluginMethods: [CAPPluginMethod] = [
        CAPPluginMethod(name: "set",    returnType: CAPPluginReturnPromise),
        CAPPluginMethod(name: "get",    returnType: CAPPluginReturnPromise),
        CAPPluginMethod(name: "remove", returnType: CAPPluginReturnPromise),
        CAPPluginMethod(name: "setProtected", returnType: CAPPluginReturnPromise),
        CAPPluginMethod(name: "getProtected", returnType: CAPPluginReturnPromise)
    ]

    private lazy var implementation = SecureStorage(
        service: Bundle.main.bundleIdentifier ?? "capacitor.securestorage"
    )


    // MARK: - Unprotected

    @objc func set(_ call: CAPPluginCall) {
        guard let key = call.getString("key") else {
            call.reject("'key' is required")
            return
        }
        guard let value = call.getString("value") else {
            call.reject("'value' is required")
            return
        }

        do {
            try implementation.set(key: key, value: value)
            call.resolve()
        } catch {
            call.reject(error.localizedDescription)
        }
    }

    @objc func get(_ call: CAPPluginCall) {
        guard let key = call.getString("key") else {
            call.reject("'key' is required")
            return
        }

        do {
            let value = try implementation.get(key: key)
            call.resolve(["value": value])
        } catch KeychainError.notFound {
            // Missing key is not an error — return null so callers can branch.
            call.resolve(["value": NSNull()])
        } catch {
            call.reject(error.localizedDescription)
        }
    }

    @objc func remove(_ call: CAPPluginCall) {
        guard let key = call.getString("key") else {
            call.reject("'key' is required")
            return
        }

        do {
            try implementation.remove(key: key)
            call.resolve()
        } catch {
            call.reject(error.localizedDescription)
        }
    }
    
    // MARK: - Biometric-protected

        @objc func setProtected(_ call: CAPPluginCall) {
            guard let key   = call.getString("key")   else { call.reject("'key' is required");   return }
            guard let value = call.getString("value") else { call.reject("'value' is required"); return }
            // Writing never triggers the biometric sheet, so no background dispatch needed.
            do {
                try implementation.setProtected(key: key, value: value)
                call.resolve()
            } catch {
                call.reject(error.localizedDescription)
            }
        }

        @objc func getProtected(_ call: CAPPluginCall) {
            guard let key = call.getString("key") else { call.reject("'key' is required"); return }
            let prompt = call.getString("prompt") ?? "Authenticate to continue"

            // keepAlive prevents Capacitor from releasing the call while the
            // biometric sheet is visible (which blocks the thread).
            call.keepAlive = true

            DispatchQueue.global(qos: .userInitiated).async { [weak self] in
                guard let self else { return }
                do {
                    let value = try self.implementation.getProtected(key: key, prompt: prompt)
                    call.resolve(["value": value])
                } catch KeychainError.notFound {
                    call.resolve(["value": NSNull()])
                } catch KeychainError.operationFailed(let status) {
                    switch status {
                    case errSecUserCanceled:   // user dismissed the sheet
                        call.reject("User cancelled authentication", "USER_CANCELLED")
                    case errSecAuthFailed:     // biometry exhausted / locked out
                        call.reject("Authentication failed", "AUTH_FAILED")
                    default:
                        call.reject("Keychain operation failed (OSStatus \(status))")
                    }
                } catch {
                    call.reject(error.localizedDescription)
                }
            }
        }
}
