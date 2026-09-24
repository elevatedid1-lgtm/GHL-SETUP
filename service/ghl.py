"""Minimal GoHighLevel API v2 client. Standard library only, so it runs in a
serverless function or a cron box without a build step.

Auth: a Private Integration Token (Settings > Private Integrations) with scopes
contacts.readonly/write, opportunities.readonly/write, locations/customFields.readonly/write.
"""

import json
import os
import urllib.error
import urllib.parse
import urllib.request

BASE_URL = "https://services.leadconnectorhq.com"
API_VERSION = "2021-07-28"


class GHLError(RuntimeError):
    def __init__(self, status, body):
        super().__init__(f"GHL API {status}: {body}")
        self.status = status
        self.body = body


class GHL:
    def __init__(self, token=None, location_id=None, dry_run=False):
        self.token = token or os.environ.get("GHL_TOKEN")
        self.location_id = location_id or os.environ.get("GHL_LOCATION_ID")
        self.dry_run = dry_run
        if not self.token:
            raise ValueError("GHL_TOKEN is not set")
        if not self.location_id:
            raise ValueError("GHL_LOCATION_ID is not set")

    def request(self, method, path, body=None, query=None):
        url = BASE_URL + path
        if query:
            url += "?" + urllib.parse.urlencode(query)
        if self.dry_run and method != "GET":
            print(f"[dry-run] {method} {path} {json.dumps(body) if body else ''}")
            return {}
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(url, data=data, method=method)
        req.add_header("Authorization", f"Bearer {self.token}")
        req.add_header("Version", API_VERSION)
        req.add_header("Accept", "application/json")
        if data is not None:
            req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                raw = resp.read()
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as e:
            raise GHLError(e.code, e.read().decode(errors="replace")) from None

    # Custom fields
    def list_custom_fields(self):
        path = f"/locations/{self.location_id}/customFields"
        return self.request("GET", path, query={"model": "all"}).get("customFields", [])

    def create_custom_field(self, name, data_type, model, options=None):
        body = {"name": name, "dataType": data_type, "model": model}
        if options:
            body["options"] = options
        return self.request("POST", f"/locations/{self.location_id}/customFields", body)

    # Contacts
    def search_contacts_by_field(self, field_id, value, limit=2):
        body = {
            "locationId": self.location_id,
            "pageLimit": limit,
            "filters": [{"field": f"customFields.{field_id}", "operator": "eq", "value": value}],
        }
        return self.request("POST", "/contacts/search", body).get("contacts", [])

    def get_contact(self, contact_id):
        return self.request("GET", f"/contacts/{contact_id}").get("contact", {})

    def update_contact(self, contact_id, custom_fields=None, tags=None):
        body = {}
        if custom_fields:
            body["customFields"] = [{"id": k, "value": v} for k, v in custom_fields.items()]
        if body:
            self.request("PUT", f"/contacts/{contact_id}", body)
        if tags:
            self.request("POST", f"/contacts/{contact_id}/tags", {"tags": tags})

    # Opportunities
    def find_opportunities(self, contact_id, pipeline_id):
        query = {"location_id": self.location_id, "contact_id": contact_id, "pipeline_id": pipeline_id}
        return self.request("GET", "/opportunities/search", query=query).get("opportunities", [])

    def move_opportunity(self, opportunity_id, stage_id):
        return self.request("PUT", f"/opportunities/{opportunity_id}", {"pipelineStageId": stage_id})

