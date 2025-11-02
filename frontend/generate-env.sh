#! /bin/sh
echo "export const environment = {production: true,imageHash : \"$1\", API_public_key:\"$2\"};" > src/environments/environment.prod.ts
if [ "$1" == "dev" ]; then
    sed -i -e 's/Zero-TOTP/Zero-TOTP dev/g' ./src/manifest.webmanifest
fi