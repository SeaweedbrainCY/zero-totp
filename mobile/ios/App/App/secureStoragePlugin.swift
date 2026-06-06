import Foundation
import Capacitor

@objc(SecureStoragePlugin)
public class SecureStoragePlugin: CAPPlugin, CAPBridgedPlugin {

    public let identifier = "SecureStoragePlugin"
    public let jsName = "iOSSecureStorage"
    public let pluginMethods: [CAPPluginMethod] = [
        CAPPluginMethod(name: "set",    returnType: CAPPluginReturnPromise),
        CAPPluginMethod(name: "get",    returnType: CAPPluginReturnPromise),
        CAPPluginMethod(name: "remove", returnType: CAPPluginReturnPromise)
    ]

    private lazy var implementation = SecureStorage(
        service: Bundle.main.bundleIdentifier ?? "capacitor.securestorage"
    )


    // MARK: - Plugin Methods

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
}
