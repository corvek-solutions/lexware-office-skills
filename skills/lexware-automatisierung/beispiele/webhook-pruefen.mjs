#!/usr/bin/env node
// webhook-pruefen.mjs · Empfänger für Lexware-Office-Webhooks mit Signaturprüfung, ohne Abhängigkeiten (Node 18+).
//
//   node webhook-pruefen.mjs            lauscht auf Port 8080 (PORT setzt einen anderen), Pfad /lexware
//
// Lexware signiert den Körper mit RSA-SHA512 und schickt die Signatur Base64-kodiert im Kopf X-Lxo-Signature.
// Ohne gültige Signatur wird nichts angenommen. Die Meldung sagt nur, welcher Datensatz sich geändert hat; was gilt,
// liest der Empfänger danach selbst bei Lexware. Antwort sofort mit 200, Arbeit danach (Lexware wartet 5 Sekunden).
// Teil der Lexware Office Skills von Corvek Solutions (MIT-Lizenz).
import { createServer } from 'node:http';
import { createPublicKey, verify } from 'node:crypto';
import { readFileSync } from 'node:fs';
import { pathToFileURL } from 'node:url';

// Öffentlicher Schlüssel von Lexware: https://developers.lexware.io/webhookSignature/public/public_key.pub
export const LEXWARE_SCHLUESSEL = `-----BEGIN PUBLIC KEY-----
MIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEAtCkZXZqT2zFRmA83KsBC
tQSv9t+AaWiZpRWvzE4wiQEh0aHzNYkT/DlP419pngqoLxnqW9SsgWfKOG3utoEV
z+Lru9odZntW/n/yaRK3f0AcMtuWs/Z1PZ4BbN/RlFYyqlPg0VfuAvZMAa+J9WAl
Fuy0T4Y0EdO0d+EL8BpzSLqj3XLI+YuK4hUhlTOxHmdDtNUkugnT9b9khb+oPDmB
3yxRP6Rmo2qo6waSc+pihCdOiZKzwA4fA1HT8DM54OaNQ4qd9NRf5uECijFlpQu6
vZdW7Z+LZ8HTgGQVSsJdCzUtM1wiWOERrHvd8IpBMvUAvGM/qaJnAmwsEr4J/El4
yCmur8wwYBtSUH0Xue42YysdmSS0pOMMUAAvr70HQMDHagYkErMtu6FAyAmPz8p/
tAqJJpwAhxITbnc5WsmZOu0Ke255nXQ/2Go1TKv+45mSb7RLsvpmhVZ4nFByFt24
vG6IwNReuLhJJL468jrdTpxyZRn0QqkxiQV7jDd9Dp1NVd/W3+n86Aos9LnJa+ut
kN+jOOWmJdJjnQetJlbDVg3ex+XHVmCjiRYggCGPlpXVJwdEUNGzxhPGKjxmeiQT
ahwFA9iHtwBw7yK5VfM/hA+JeF2FXYhTdehfClAQt1YCYXkgUEFxm9idRdBoCY6U
bmFUXQLdi7tZyDor8Rxoq2MCAwEAAQ==
-----END PUBLIC KEY-----
`;

// Nur für Tests: eigener Schlüssel aus einer Datei
const schluessel = createPublicKey(process.env.LEXWARE_WEBHOOK_TESTSCHLUESSEL
  ? readFileSync(process.env.LEXWARE_WEBHOOK_TESTSCHLUESSEL, 'utf8') : LEXWARE_SCHLUESSEL);

const MAX = 4096;
const KENNUNG = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

/** true, wenn die Signatur zum Körper passt (wie angekommen oder in kompakter JSON-Form) */
export function signaturGueltig(koerper, signatur, key = schluessel) {
  if (!signatur || signatur.length > 2048 || !/^[A-Za-z0-9+/=\s]+$/.test(signatur)) return false;
  const sig = Buffer.from(signatur.replace(/\s/g, ''), 'base64');
  try {
    if (verify('RSA-SHA512', koerper, key, sig)) return true;
    const kompakt = Buffer.from(JSON.stringify(JSON.parse(koerper.toString('utf8'))));
    return !kompakt.equals(koerper) && verify('RSA-SHA512', kompakt, key, sig);
  } catch {
    return false;
  }
}

/** Nur die vier bekannten Felder, streng geprüft; alles andere ist kein Lexware-Ereignis */
export function ereignisLesen(koerper) {
  const d = JSON.parse(koerper.toString('utf8'));
  if (!KENNUNG.test(d.organizationId ?? '') || !KENNUNG.test(d.resourceId ?? '')) return null;
  if (typeof d.eventType !== 'string' || !/^[a-z-]+(\.[a-z]+){1,2}$/.test(d.eventType)) return null;
  return { organizationId: d.organizationId, eventType: d.eventType, resourceId: d.resourceId, eventDate: String(d.eventDate ?? '') };
}

/** Hier die eigentliche Arbeit: Datensatz bei Lexware nachlesen (lexware.py get /invoices/<resourceId>) usw. */
async function verarbeiten(e) {
  console.log(new Date().toISOString(), e.eventType, e.resourceId);
}

export function starten(port = Number(process.env.PORT ?? 8080)) {
  const server = createServer((req, res) => {
    if (req.url !== '/lexware') { res.writeHead(404).end(); return; }
    if (req.method === 'HEAD') { res.writeHead(200).end(); return; }   // Lexware prüft die Adresse beim Einrichten
    if (req.method !== 'POST') { res.writeHead(405).end(); return; }
    const teile = []; let groesse = 0;
    req.on('data', (c) => { groesse += c.length; if (groesse > MAX) req.destroy(); else teile.push(c); });
    req.on('end', () => {
      const koerper = Buffer.concat(teile);
      if (!signaturGueltig(koerper, req.headers['x-lxo-signature'])) { res.writeHead(401).end(); return; }
      let e = null;
      try { e = ereignisLesen(koerper); } catch { /* kein JSON */ }
      res.writeHead(200).end();                // sofort bestätigen, Arbeit danach
      if (e) verarbeiten(e).catch((f) => console.error('Fehler bei', e.eventType, f.message));
    });
  });
  server.listen(port, () => console.log(`Lexware-Webhook lauscht auf :${server.address().port}/lexware`));
  return server;
}

if (import.meta.url === pathToFileURL(process.argv[1] ?? '').href) starten();
