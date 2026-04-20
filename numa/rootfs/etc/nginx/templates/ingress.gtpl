server {
    listen {{ .interface }}:{{ .port }} default_server;

    include /etc/nginx/includes/server_params.conf;
    include /etc/nginx/includes/proxy_params.conf;

    location / {
        allow   172.30.32.2;
        deny    all;

        # sub_filter applies to HTML by default; also enable for CSS so that
        # @font-face url() references inside fonts.css get rewritten too.
        sub_filter_types text/css;

        # Replace every occurrence of each pattern (the font-face block in
        # fonts.css has five absolute /fonts/… url() entries).
        sub_filter_once off;

        # Patch the Numa dashboard JS so API calls use the Ingress path prefix.
        # HA Ingress injects X-Ingress-Path on every request; nginx makes it
        # available as $http_x_ingress_path which we embed into the HTML.
        sub_filter "const API = '';" "const API = '$http_x_ingress_path';";

        # Patch absolute /fonts/ references so they are resolved through the
        # ingress prefix rather than the HA root.
        #
        # Without this, the browser turns href="/fonts/fonts.css" into
        # http://homeassistant.local:8123/fonts/fonts.css (missing the ingress
        # path segment) and gets a 404.  The same applies to every url(/fonts/…)
        # entry inside fonts.css itself.
        sub_filter 'href="/fonts/'  'href="$http_x_ingress_path/fonts/';
        sub_filter "href='/fonts/"  "href='$http_x_ingress_path/fonts/";
        sub_filter 'url(/fonts/'    'url($http_x_ingress_path/fonts/';

        proxy_pass http://numa_backend;
    }
}
