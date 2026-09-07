# Substitute $SERVER_NA_NAME for the value of the environment variable SERVER_NA_NAME in nginx conf

echo "Setting up reverse proxy for $SERVER_NA_NAME"

mv /etc/nginx/nginx.reverseproxy.conf.disabled /etc/nginx/conf.d/default.conf
sed -i "s/SERVER_NA_NAME/$SERVER_NA_NAME/g" /etc/nginx/conf.d/default.conf

nginx -g "daemon off;"