/**
 * Cloudflare Pages Function — Safe edge proxy for NASA OSDR search API
 * Resolves browser CORS restriction (osdr.nasa.gov sets ACAO: osdr.nasa.gov)
 * with short edge caching and clean error payload fallback.
 */
export async function onRequestGet(context) {
  const url = new URL(context.request.url);
  const term = (url.searchParams.get('term') || 'radiation astronaut').slice(0, 80);
  const size = Math.min(6, Math.max(1, parseInt(url.searchParams.get('size') || '4', 10) || 4));
  const upstream = `https://osdr.nasa.gov/osdr/data/search?term=${encodeURIComponent(term)}&from=0&size=${size}&type=cgene`;

  try {
    const resp = await fetch(upstream, {
      headers: { 'User-Agent': 'AstroSoma-Pages-Edge/1.0' },
      cf: { cacheTtl: 1800, cacheEverything: true },
    });
    if (!resp.ok) {
      return new Response(JSON.stringify({ ok: false, status: resp.status }), {
        status: 502,
        headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
      });
    }
    const raw = await resp.json();
    const hits = ((raw.hits && raw.hits.hits) || []).map((h) => {
      const s = h._source || {};
      const acc = String(s.Accession || '').trim();
      return {
        accession: acc,
        title: String(s['Study Title'] || '').trim(),
        organism: String(s.organism || '').trim(),
        project_type: String(s['Project Type'] || '').trim(),
        url: acc ? `https://osdr.nasa.gov/bio/repo/data/studies/${acc}` : 'https://osdr.nasa.gov/bio/repo/',
      };
    });
    return new Response(JSON.stringify({ ok: true, term, studies: hits }), {
      status: 200,
      headers: {
        'Content-Type': 'application/json; charset=utf-8',
        'Access-Control-Allow-Origin': '*',
        'Cache-Control': 'public, max-age=1800',
      },
    });
  } catch (err) {
    return new Response(JSON.stringify({ ok: false, error: 'upstream_unavailable' }), {
      status: 502,
      headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
    });
  }
}
