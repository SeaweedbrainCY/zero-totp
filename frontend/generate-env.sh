#! /bin/bash
echo "export const environment = {production: true,imageHash : \"$1\", API_public_key:\"$2\"};" > src/environments/environment.prod.ts