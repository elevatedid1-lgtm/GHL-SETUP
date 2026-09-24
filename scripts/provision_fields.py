"""Create the custom fields in config/ghl-schema.json that don't exist yet.

Idempotent: matches on fieldKey, never edits or deletes an existing field.
Dry run is the default; pass --apply to write.

    GHL_TOKEN=pit-... GHL_LOCATION_ID=Evfk5CgjxNHryw79uGDD python3 scripts/provision_fields.py
    ... --apply

What it will not do (GHL's API or good sense won't allow it):
  * change an existing field's type (TEXT -> DATE). Create the replacement, migrate, then
    delete the old one in the UI once no workflow, form or smart list references it.
  * rename a key. Keys are permanent; only display names change, in the UI.
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from service.ghl import GHL  # noqa: E402
from service.referral_sync import load_schema  # noqa: E402


def key_from_name(model, name):
    """GHL derives the key from the display name: lowercase, non-alphanumerics -> '_'."""
    slug = "".join(c if c.isalnum() else "_" for c in name.lower())
    while "__" in slug:
        slug = slug.replace("__", "_")
    return f"{model}.{slug.strip('_')}"


def missing_fields(schema, live_fields):
    live_keys = {f["fieldKey"] for f in live_fields}
    todo = []
    for f in schema["customFields"]:
        if f["status"] != "create" or f["key"] in live_keys:
            continue
        if key_from_name(f["model"], f["name"]) != f["key"]:
            raise ValueError(f"{f['name']!r} would get key {key_from_name(f['model'], f['name'])!r}, "
                             f"schema says {f['key']!r}. Fix the schema so code and GHL agree.")
        todo.append(f)
    return todo


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="actually create the fields")
    args = ap.parse_args()

    schema = load_schema()
    client = GHL(location_id=schema["locationId"], dry_run=not args.apply)
    todo = missing_fields(schema, client.list_custom_fields())
    if not todo:
        print("Nothing to create. Live account matches config/ghl-schema.json.")
        return
    for f in todo:
        opts = [o for o in f.get("options", []) if not o.startswith("(")]
        client.create_custom_field(f["name"], f["dataType"], f["model"], options=opts or None)
        print(f"{'created' if args.apply else 'would create'}: {f['key']} ({f['dataType']})")
    if not args.apply:
        print(f"\n{len(todo)} field(s). Re-run with --apply to create them.")
        return
    # GHL generates the key server-side. Verify it matches, because every workflow,
    # merge tag and the sync service reference the key, not the display name.
    live_keys = {f["fieldKey"] for f in client.list_custom_fields()}
    drift = [f["key"] for f in todo if f["key"] not in live_keys]
    if drift:
        sys.exit(f"Created, but these keys did not come out as expected: {drift}. "
                 "Check the field in Settings > Custom Fields and update config/ghl-schema.json.")


if __name__ == "__main__":
    main()
