#!/bin/sh

# Extraer el primer nameserver de /etc/resolv.conf
RESOLVER=$(grep -i nameserver /etc/resolv.conf | head -n1 | cut -d' ' -f2)

# Si no se encuentra un resolver, usar 8.8.8.8 como fallback seguro
if [ -z "$RESOLVER" ]; then
  RESOLVER="8.8.8.8"
fi

# Si es una direccion IPv6 (contiene dos puntos), debe envolverse en corchetes para NGINX
if echo "$RESOLVER" | grep -q ":"; then
  RESOLVER="[$RESOLVER]"
fi

echo "DNS resolver detectado y formateado para NGINX: $RESOLVER"

# Reemplazar el marcador en el archivo de configuracion
sed -i "s/DNS_RESOLVER_IP/$RESOLVER/g" /etc/nginx/nginx.conf

echo "Iniciando NGINX..."
exec nginx -g "daemon off;"
