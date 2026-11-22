// Test für skills/lexware-automatisierung/beispiele/webhook-pruefen.mjs:  node --test tests/
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { generateKeyPairSync, sign } from 'node:crypto';
import { writeFileSync, mkdtempSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

const { publicKey, privateKey } = generateKeyPairSync('rsa', { modulusLength: 2048 });
const datei = join(mkdtempSync(join(tmpdir(), 'lxw-')), 'test.pub');
writeFileSync(datei, publicKey.export({ type: 'spki', format: 'pem' }));
process.env.LEXWARE_WEBHOOK_TESTSCHLUESSEL = datei;
const { starten, signaturGueltig } = await import('../skills/lexware-automatisierung/beispiele/webhook-pruefen.mjs');

const koerper = JSON.stringify({ organizationId: 'aa2b6f8f-0d6d-4f3e-9f0e-1c2d3e4f5a6b', eventType: 'invoice.status.changed',
  resourceId: 'bb2b6f8f-0d6d-4f3e-9f0e-1c2d3e4f5a6b', eventDate: '2026-11-22T10:00:00.000+01:00' });
const signatur = sign('RSA-SHA512', Buffer.from(koerper), privateKey).toString('base64');

test('Signatur gültig und ungültig', () => {
  assert.equal(signaturGueltig(Buffer.from(koerper), signatur), true);
  assert.equal(signaturGueltig(Buffer.from(koerper.replace('invoice', 'quotation')), signatur), false);
  assert.equal(signaturGueltig(Buffer.from(koerper), undefined), false);
});

test('Server: HEAD 200, gültig 200, gefälscht 401', async () => {
  const server = starten(0);
  await new Promise((r) => server.once('listening', r));
  const url = `http://127.0.0.1:${server.address().port}/lexware`;
  assert.equal((await fetch(url, { method: 'HEAD' })).status, 200);
  assert.equal((await fetch(url, { method: 'POST', body: koerper, headers: { 'x-lxo-signature': signatur } })).status, 200);
  assert.equal((await fetch(url, { method: 'POST', body: koerper, headers: { 'x-lxo-signature': 'AAAA' } })).status, 401);
  server.close();
});
