"""JuniorStoneField access covenant — private land requires owner word of consent."""
from __future__ import annotations

TERMS_VERSION = "jsf-covenant-2026-08-30"

TERMS_TEXT = """JuniorStoneField Access Covenant

1. What this space is
JuniorStoneField is the climbing knowledge and teaching product inside JuniorClimbs.
It covers public outdoor fields, gym walls, camps, and classes. It is not a dump of
other apps' guidebooks.

2. Private land
Do not submit boulders, GPS pins, topos, photos, or beta that sit on private land
unless the landowner — or someone with authority to speak for the owner — has given
word of consent that the information may be uploaded and made available to the public.

Without that consent:
  - the pin must not be posted as public,
  - the record is rejected or kept visibility=private,
  - JuniorCloud will not treat "I found it" as permission.

3. Unknown tenure
If you do not know whether the rock is public or private, treat it as private until
you can say. Flag tenure=unknown. Do not publish coordinates as a public node.

4. Public land is not a free-for-all
OSMP, USFS, BLM, state parks, and county open space still have parking rules, seasonal
closures, raptor closures, and fire restrictions. Posting a public-land pin does not
waive those rules.

5. Gyms and camps
Indoor sets, camp curricula, and class plans default to visibility=gym_internal.
They are for the gym's programs unless staff mark them public.

6. Community licenses
Route text you import through JuniorSourceLedger must carry CC0, CC-BY, CC-BY-SA, or
public-domain. Closed commercial beta is not copied here.

7. Takedown
Landowner or managing agency can request removal. Local operators should honor that
word the same day the request is logged.

Version: jsf-covenant-2026-08-30
"""

PUBLIC_TENURE = {"public", "usfs", "blm", "nps", "osmp", "state", "county", "gym"}


def outdoor_publish_allowed(tenure: str, owner_consent: bool, visibility: str) -> tuple[bool, str]:
    t = (tenure or "unknown").lower()
    vis = (visibility or "public").lower()
    if vis in {"private", "gym_internal"}:
        return True, "stored_non_public"
    if t in PUBLIC_TENURE or t == "gym":
        return True, "public_or_gym"
    if t in {"private", "unknown", "ranch", "inholding"} and not owner_consent:
        return False, "private_or_unknown_land_requires_owner_consent_to_publish"
    if owner_consent:
        return True, "owner_consent_on_record"
    return False, "consent_required"
