USE zero_totp;

-- Création de la table "User" si elle n'existe pas déjà
CREATE TABLE IF NOT EXISTS User (
    id INT AUTO_INCREMENT PRIMARY KEY,
    mail VARCHAR(256) NOT NULL,
    password VARCHAR(256) NOT NULL,
    username VARCHAR(256) NOT NULL,
    derivedKeySalt VARCHAR(256) NOT NULL
);

-- Création de la table "ZKE_encryption_key" si elle n'existe pas déjà
CREATE TABLE IF NOT EXISTS ZKE_encryption_key (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    ZKE_key VARCHAR(256) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES User(id)
);

-- Création de la table "Vaults" si elle n'existe pas déjà
CREATE TABLE IF NOT EXISTS Vaults (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    enc_vault TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES User(id)
);