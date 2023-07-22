#! /bin/bash
echo "export const environment = {production: true,API_URL : \"https://api.zero-totp.com\",imageHash : \"$1\"};" > src/environments/environment.prod.ts