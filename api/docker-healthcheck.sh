health=$(curl --fail --silent http://127.0.0.1:8080/api/v1/healthcheck | jq .health)
if [ "$health" = "\"OK\"" ]; then
  exit 0
else
  exit 1
fi