from environment import conf, logging
from flask import Response


# GET /privacy-policy
def get_privacy_policy(lang="en"):
    try:
        if lang not in conf.features.privacy_policy.available_languages:
            logging.warning(f"Requested privacy policy language '{lang}' is not available. Defaulting to 'en'.")
            lang = "en"
        with open(conf.features.privacy_policy.privacy_policy_mk_file_path[lang], "r") as f:
            privacy_policy = f.read()
        return Response(
            privacy_policy,
            mimetype="text/markdown",
            headers={"Content-Disposition": "inline; filename=privacy_policy.md"}
        )
    except Exception as e:
        logging.error("Error while reading privacy policy file: " + str(e))
        return {"message": "No privacy policy defined for this instance."}, 404


# GET /configuration
def get_configuration():
    config_data = {
        "signup_enabled": bool(conf.features.signup_enabled),
    }
    return config_data, 200