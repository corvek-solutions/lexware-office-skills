"""Test für skills/lexware-check/scripts/check.py gegen eine Lexware-Attrappe mit typischen Schwachstellen."""
import datetime as dt
import http.server
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import threading
import unittest

CHECK = pathlib.Path(__file__).resolve().parents[1] / "skills" / "lexware-check" / "scripts" / "check.py"
HEUTE = dt.date.today()


def tag(vor: int) -> str:
    return f"{HEUTE - dt.timedelta(days=vor)}T00:00:00.000+01:00"


KONTAKTE = [
    {"id": "1", "roles": {"customer": {"number": 10001}}, "company": {"name": "Muster Bau GmbH"},
     "addresses": {"billing": [{"city": "Frankfurt"}]}},
    {"id": "2", "roles": {"customer": {"number": 10002}}, "company": {"name": "Muster Bau"},
     "addresses": {"billing": [{"city": "Frankfurt"}]}},
    {"id": "3", "roles": {"customer": {"number": 10003}}, "company": {"name": "Hausverwaltung Beispiel"},
     "addresses": {"billing": [{"city": "Mainz"}, {"city": "Wiesbaden"}]}},
    {"id": "4", "roles": {"customer": {"number": 10004}}, "person": {"firstName": "Eva", "lastName": "Probe"},
     "addresses": {}},
    {"id": "5", "roles": {"vendor": {"number": 70001}}, "company": {"name": "Lieferant AG"}, "addresses": {}},
]
ARTIKEL = [{"title": "Fliesen verlegen", "unitName": "m²", "articleNumber": "LV-1"},
           {"title": "Silikonfuge", "unitName": "lfdm", "articleNumber": "LV-1"},
           {"title": "Kleinmaterial", "unitName": "Stk"},
           {"title": "Anfahrt", "unitName": "St."},
           {"title": "Montage", "unitName": "Stück"}]
OFFEN = [{"voucherNumber": f"RE-{i}", "contactName": "Muster Bau GmbH", "dueDate": tag(300 if i < 6 else 5),
          "voucherStatus": "overdue" if i < 6 else "open"} for i in range(8)]


class Attrappe(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def antwort(self, d, status=200):
        roh = json.dumps(d).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(roh)))
        self.end_headers()
        self.wfile.write(roh)

    def do_GET(self):
        p, _, q = self.path.partition("?")
        params = dict(x.split("=", 1) for x in q.split("&") if "=" in x)
        if p == "/v1/profile":
            return self.antwort({"companyName": "Muster Sanierung GmbH", "taxType": "net", "smallBusiness": False})
        if p == "/v1/contacts":
            return self.antwort({"content": KONTAKTE, "last": True})
        if p == "/v1/articles":
            return self.antwort({"content": ARTIKEL, "last": True})
        if p == "/v1/voucherlist":
            if params.get("voucherStatus") == "draft":
                return self.antwort({"content": [{"voucherType": "invoice", "contactName": "Eva Probe",
                                                  "voucherDate": tag(60)}], "last": True})
            if params.get("voucherType") == "invoice":
                return self.antwort({"content": OFFEN, "last": True})
            return self.antwort({"content": [{"voucherStatus": "overdue"}, {"voucherStatus": "overdue"},
                                             {"voucherStatus": "open"}], "last": True})
        if p == "/v1/event-subscriptions":
            return self.antwort({"content": []})
        return self.antwort({"message": "nicht gefunden"}, 404)

    def do_POST(self):
        self.antwort({"message": "dieser Check darf nie schreiben"}, 500)
        raise AssertionError("POST im Check")


class TestCheck(unittest.TestCase):
    def test_bericht(self):
        server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Attrappe)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        with tempfile.TemporaryDirectory() as tmp:
            env = dict(os.environ, LEXWARE_BASIS=f"http://127.0.0.1:{server.server_port}/v1", LEXWARE_API_KEY="t",
                       XDG_CACHE_HOME=tmp, HOME=tmp)
            r = subprocess.run([sys.executable, "-I", str(CHECK)], capture_output=True, text=True, env=env, timeout=60)
        server.shutdown()
        server.server_close()
        self.assertEqual(r.returncode, 0, r.stderr)
        b = r.stdout
        self.assertIn("# Lexware-Check: Muster Sanierung GmbH", b)
        self.assertIn("🔴 Kunden mit mehreren Rechnungsadressen", b)
        self.assertIn("Hausverwaltung Beispiel", b)
        self.assertIn("🟡 Kunden ohne Rechnungsadresse", b)
        self.assertIn("Muster Bau GmbH = Muster Bau", b)
        self.assertIn("🔴 Doppelte Artikelnummern", b)
        self.assertIn("Stück: St., Stk, Stück", b)
        self.assertIn("🔴 Zahlungsabgleich fehlt vermutlich", b)
        self.assertIn("🟡 Alte Entwürfe", b)
        self.assertIn("🟡 Viele abgelaufene Angebote", b)
        self.assertIn("Gesamt: 🔴", b)


if __name__ == "__main__":
    unittest.main()
