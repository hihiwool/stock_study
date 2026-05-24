const jsonHeaders = {
  "content-type": "application/json; charset=utf-8",
  "cache-control": "no-store",
};

function json(data, init = {}) {
  return new Response(JSON.stringify(data, null, 2), {
    ...init,
    headers: {
      ...jsonHeaders,
      ...(init.headers || {}),
    },
  });
}

export default {
  async fetch(request) {
    const url = new URL(request.url);

    if (request.method === "OPTIONS") {
      return new Response(null, {
        status: 204,
        headers: {
          "access-control-allow-origin": "https://stock.howlnode.com",
          "access-control-allow-methods": "GET,POST,OPTIONS",
          "access-control-allow-headers": "content-type,authorization",
          "access-control-max-age": "86400",
        },
      });
    }

    if (url.pathname === "/" || url.pathname === "/health") {
      return json({
        ok: true,
        service: "stock-study-api",
        purpose: "Broker API proxy placeholder. No broker secrets are stored yet.",
      });
    }

    if (url.pathname.startsWith("/broker/")) {
      return json(
        {
          ok: false,
          error: "broker_api_not_configured",
          message: "Add broker API credentials as Worker secrets before enabling this endpoint.",
        },
        { status: 501 },
      );
    }

    return json({ ok: false, error: "not_found" }, { status: 404 });
  },
};

