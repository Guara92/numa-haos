server {
    listen {{ .interface }}:{{ .port }} default_server;

    include /etc/nginx/includes/server_params.conf;
    include /etc/nginx/includes/proxy_params.conf;

    location / {
        allow   172.30.32.2;
        deny    all;

        # Patch the Numa dashboard JS so API calls use the Ingress path prefix.
        # HA Ingress injects X-Ingress-Path on every request; nginx makes it
        # available as $http_x_ingress_path which we embed into the HTML.
        sub_filter "const API = '';" "const API = '$http_x_ingress_path';";
        sub_filter_once on;
        sub_filter_types text/html;

        proxy_pass http://numa_backend;
    }
}
