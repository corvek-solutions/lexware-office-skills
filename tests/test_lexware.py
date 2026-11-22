"""Tests für skills/lexware-grundlagen/scripts/lexware.py gegen eine Lexware-Attrappe auf 127.0.0.1.

    python3 -m unittest discover -s tests -v

Kein echtes Lexware-Konto nötig. Nur Standardbibliothek.
"""
import http.server
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import threading
import unittest

WERKZEUG = pathlib.Path(__file__).resolve().parents[1] / "skills" / "lexware-grundlagen" / "scripts" / "lexware.py"


class Attrappe(http.server.BaseHTTPRequestHandler):
    anfragen: list = []
    zaehler: dict = {}

    def log_message(self, *a):
        pass

    def _antwort(self, status, daten=None, typ="application/json", kopf=None):
        roh = daten if isinstance(daten, bytes) else (json.dumps(daten).encode() if daten is not None else b"")
        self.send_response(status)
        self.send_header("Content-Type", typ)
        for k, v in (kopf or {}).items():
            self.send_header(k, v)
        self.send_header("Content-Length", str(len(roh)))
        self.end_headers()
        self.wfile.write(roh)

    def _merken(self):
        laenge = int(self.headers.get("Content-Length") or 0)
        koerper = self.rfile.read(laenge) if laenge else b""
        Attrappe.anfragen.append((self.command, self.path, self.headers.get("Authorization"), koerper))
        return koerper

    def do_GET(self):
        self._merken()
        p = self.path
        if p.startswith("/v1/profile"):
            return self._antwort(200, {"companyName": "Muster Bau GmbH", "taxType": "net", "smallBusiness": False})
        if p.startswith("/v1/voucherlist"):
            seite = int(dict(x.split("=") for x in p.split("?")[1].split("&")).get("page", 0))
            inhalt = [{"voucherNumber": f"RE{seite}{i}", "contactName": "Muster", "openAmount": 119.0} for i in range(2)]
            return self._antwort(200, {"content": inhalt, "totalPages": 2, "last": seite == 1})
        if p.startswith("/v1/contacts"):
            n = Attrappe.zaehler.get("contacts", 0)
            Attrappe.zaehler["contacts"] = n + 1
            if n == 0:
                return self._antwort(429, {"message": "Rate limit exceeded"}, kopf={"Retry-After": "1"})
            return self._antwort(200, {"content": [{"id": "k1", "company": {"name": "Muster Bau GmbH"}}], "last": True})
        if p.endswith("/file"):
            if "xml" in (self.headers.get("Accept") or ""):
                return self._antwort(200, b'<?xml version="1.0"?><Invoice/>', typ="application/xml")
            return self._antwort(200, b"%PDF-1.7 test", typ="application/pdf")
        if p.startswith("/v1/kaputt"):
            return self._antwort(503, {"message": "kurz weg"})
        return self._antwort(404, {"message": "not found"})

    def do_POST(self):
        koerper = self._merken()
        if self.path.startswith("/v1/files"):
            ok = b'name="type"' in koerper and b"voucher" in koerper and b'filename="beleg.pdf"' in koerper
            return self._antwort(202 if ok else 400, {"id": "f1"} if ok else {"message": "multipart"})
        if self.path.startswith("/v1/invoices"):
            d = json.loads(koerper or b"{}")
            if any(len(x.get("name", "")) > 100 for x in d.get("lineItems", [])):
                return self._antwort(406, {"message": "Validation failed", "details": [
                    {"violation": "SIZE", "field": "lineItems[0].name", "message": "Größe muss zwischen 1 und 100 sein"}]})
            return self._antwort(201, {"id": "11111111-2222-3333-4444-555555555555", "version": 1})
        return self._antwort(404, {})

    do_PUT = do_POST

    def do_DELETE(self):
        self._merken()
        return self._antwort(204)


class TestLexware(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Attrappe)
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()
        cls.tmp = tempfile.TemporaryDirectory()
        cls.env = dict(os.environ, LEXWARE_BASIS=f"http://127.0.0.1:{cls.server.server_port}/v1",
                       LEXWARE_API_KEY="test-schluessel-48-zeichen-xxxxxxxxxxxxxxxxxxxxxx",
                       XDG_CACHE_HOME=cls.tmp.name, HOME=cls.tmp.name)
        cls.env.pop("LEXWARE_NUR_LESEN", None)

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.tmp.cleanup()

    def setUp(self):
        Attrappe.anfragen.clear()
        Attrappe.zaehler.clear()

    def lauf(self, *args, env=None, eingabe=None):
        return subprocess.run([sys.executable, "-I", str(WERKZEUG), *args], capture_output=True, text=True,
                              env=env or self.env, input=eingabe, timeout=60)

    def test_pruefen(self):
        r = self.lauf("pruefen")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(json.loads(r.stdout)["firma"], "Muster Bau GmbH")
        self.assertEqual(Attrappe.anfragen[0][2], "Bearer " + self.env["LEXWARE_API_KEY"])

    def test_schluessel_nie_in_ausgabe(self):
        r = self.lauf("get", "/gibtsnicht")
        self.assertNotIn(self.env["LEXWARE_API_KEY"], r.stdout + r.stderr)

    def test_429_wartet_und_wiederholt(self):
        r = self.lauf("get", "/contacts", "name=Muster")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("429", r.stderr)
        self.assertEqual(len([a for a in Attrappe.anfragen if a[1].startswith("/v1/contacts")]), 2)

    def test_alle_seiten_mit_feldern_und_csv(self):
        r = self.lauf("alle", "/voucherlist", "voucherType=invoice", "voucherStatus=open",
                      "--felder", "voucherNumber,openAmount", "--csv")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout.strip().splitlines(), ["voucherNumber;openAmount", "RE00;119.0", "RE01;119.0",
                                                         "RE10;119.0", "RE11;119.0"])
        self.assertIn("size=250", Attrappe.anfragen[0][1])

    def test_406_nennt_feld_und_wiederholt_nicht(self):
        r = self.lauf("post", "/invoices", "-", eingabe=json.dumps({"lineItems": [{"name": "x" * 101}]}))
        self.assertEqual(r.returncode, 2)
        self.assertIn("lineItems[0].name", r.stderr)
        self.assertEqual(len(Attrappe.anfragen), 1)

    def test_entwurf_mit_link(self):
        r = self.lauf("post", "/invoices", "-", eingabe=json.dumps({"lineItems": [{"name": "Beratung"}]}))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(json.loads(r.stdout)["link"].endswith("/invoices/edit/11111111-2222-3333-4444-555555555555"))

    def test_festschreiben_gesperrt(self):
        r = self.lauf("post", "/invoices", "-", "finalize=true", eingabe="{}")
        self.assertEqual(r.returncode, 3)
        self.assertEqual(Attrappe.anfragen, [])

    def test_festschreiben_mit_schalter(self):
        r = self.lauf("post", "/invoices", "-", "finalize=true", "--festschreiben",
                      eingabe=json.dumps({"lineItems": []}))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("finalize=true", Attrappe.anfragen[0][1])

    def test_nur_lesen(self):
        r = self.lauf("post", "/invoices", "-", eingabe="{}", env=dict(self.env, LEXWARE_NUR_LESEN="1"))
        self.assertEqual(r.returncode, 3)
        self.assertEqual(Attrappe.anfragen, [])

    def test_put_braucht_version(self):
        r = self.lauf("put", "/contacts/abc", "-", eingabe="{}")
        self.assertEqual(r.returncode, 2)
        self.assertEqual(Attrappe.anfragen, [])

    def test_loeschen_nur_artikel_und_mit_ja(self):
        self.assertEqual(self.lauf("loeschen", "/invoices/11111111-2222-3333-4444-555555555555", "--ja").returncode, 3)
        self.assertEqual(self.lauf("loeschen", "/articles/11111111-2222-3333-4444-555555555555").returncode, 3)
        r = self.lauf("loeschen", "/articles/11111111-2222-3333-4444-555555555555", "--ja")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual([a[0] for a in Attrappe.anfragen], ["DELETE"])

    def test_pdf(self):
        ziel = pathlib.Path(self.tmp.name) / "re.pdf"
        r = self.lauf("pdf", "invoice", "11111111-2222-3333-4444-555555555555", str(ziel))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(ziel.read_bytes().startswith(b"%PDF-"))

    def test_hochladen(self):
        beleg = pathlib.Path(self.tmp.name) / "beleg.pdf"
        beleg.write_bytes(b"%PDF-1.4 beleg")
        r = self.lauf("hochladen", str(beleg))
        self.assertEqual(r.returncode, 0, r.stderr)
        zu_gross = pathlib.Path(self.tmp.name) / "gross.pdf"
        zu_gross.write_bytes(b"%PDF-" + b"0" * (5 * 1024 * 1024 + 1))
        self.assertEqual(self.lauf("hochladen", str(zu_gross)).returncode, 2)

    def test_schreiben_bei_stoerung_nicht_wiederholt(self):
        r = self.lauf("get", "/kaputt")
        self.assertEqual(len(Attrappe.anfragen), 4)  # Lesen: 1 + 3 Wiederholungen
        Attrappe.anfragen.clear()
        r = self.lauf("post", "/kaputt", "-", eingabe="{}")
        self.assertNotEqual(r.returncode, 0)
        self.assertEqual(len(Attrappe.anfragen), 1)

    def test_datum_mit_berliner_versatz(self):
        self.assertEqual(self.lauf("datum", "2026-11-12").stdout.strip(), "2026-11-12T00:00:00.000+01:00")
        self.assertEqual(self.lauf("datum", "2026-07-01").stdout.strip(), "2026-07-01T00:00:00.000+02:00")

    def test_fremde_adresse_wird_ignoriert(self):
        env = dict(self.env, LEXWARE_BASIS="https://evil.example/v1", LEXWARE_API_KEY="x")
        out = subprocess.run([sys.executable, "-I", "-c",
                              f"import sys; sys.path.insert(0, {str(WERKZEUG.parent)!r}); import lexware; print(lexware.basis())"],
                             capture_output=True, text=True, env=env)
        self.assertEqual(out.stdout.strip(), "https://api.lexware.io/v1")

    def test_belegliste_braucht_art_und_status(self):
        r = self.lauf("get", "/voucherlist", "voucherType=invoice")
        self.assertEqual(r.returncode, 2)
        r = self.lauf("get", "/voucherlist", "voucherType=invoice", "voucherStatus=open,overdue")
        self.assertEqual(r.returncode, 2)
        self.assertEqual(Attrappe.anfragen, [])

    def test_kontaktsuche_kodiert(self):
        self.lauf("get", "/contacts", "name=Müller & Söhne")
        pfade = [a[1] for a in Attrappe.anfragen]
        self.assertTrue(any("name=M%C3%BCller+%26amp%3B+S%C3%B6hne" in p for p in pfade), pfade)
        self.assertEqual(self.lauf("get", "/contacts", "name=ab").returncode, 2)

    def test_xrechnung_als_xml(self):
        ziel = pathlib.Path(self.tmp.name) / "re.xml"
        r = self.lauf("pdf", "invoice", "11111111-2222-3333-4444-555555555555", str(ziel), "--xml")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(ziel.read_bytes().startswith(b"<?xml"))

    def test_link(self):
        r = self.lauf("link", "quotation", "abc")
        self.assertEqual(r.stdout.strip(), "https://app.lexware.de/permalink/quotations/view/abc")


if __name__ == "__main__":
    unittest.main()
