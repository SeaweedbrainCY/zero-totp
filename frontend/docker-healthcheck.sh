curl --fail --silent http://127.0.0.1:80
if [ "$?" -eq "0" ]; then
  exit 0
else
  exit 1
fi