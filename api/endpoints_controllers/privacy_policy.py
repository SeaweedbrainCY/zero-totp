from environment import conf, logging


# GET /privacy-policy
def get_privacy_policy(lang="en"):
    try:
        if lang not in conf.features.privacy_policy.available_languages:
            logging.warning(f"Requested privacy policy language '{lang}' is not available. Defaulting to 'en'.")
            lang = "en"
        with open(conf.features.privacy_policy.privacy_policy_mk_file_path[lang], "r") as f:
            privacy_policy = f.read()
        return {"markdown": privacy_policy}, 200
    except Exception as e:
        logging.error("Error while reading privacy policy file: " + str(e))
        return {"message": "No privacy policy defined for this instance."}, 404