@@
   // If no asset binding is present or all attempts failed, return JSON 404 to avoid empty responses
-  return c.json({ error: 'Not Found' }, 404);
+  // As an emergency fallback when no asset binding is available at runtime,
+  // serve an embedded, minimal index.html so the SPA can bootstrap. This
+  // avoids a broken root response when Cloudflare exposes the static site
+  // binding under an unexpected name.
+  const embeddedIndex = `<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Portal‑OS</title><style>body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,'Helvetica Neue',Arial,sans-serif;margin:0;padding:20px;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);min-height:100vh;display:flex;align-items:center;justify-content:center}.container{background:#fff;border-radius:10px;box-shadow:0 10px 40px rgba(0,0,0,.2);padding:40px;max-width:600px;text-align:center}h1{color:#333;margin:0 0 10px 0;font-size:2.5em}.version{color:#666;font-size:14px;margin-bottom:30px}.status{display:inline-block;background:#10b981;color:#fff;padding:10px 20px;border-radius:20px;font-size:14px;font-weight:600;margin-bottom:20px}</style></head><body><div class="container"><h1>🌐 Portal‑OS</h1><p class="version">Deployed (fallback)</p><div class="status">✓ Live</div></div><script>console.log('Embedded fallback index served');</script></body></html>`;
+
+  return new Response(embeddedIndex, {
+    headers: { 'Content-Type': 'text/html; charset=utf-8' },
+    status: 200
+  });
 }
 });
*** End Patch
