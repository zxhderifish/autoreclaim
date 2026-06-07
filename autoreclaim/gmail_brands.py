from __future__ import annotations

import tldextract

# Public mailbox providers — their domain is not a "brand the user uses".
PUBLIC_EMAIL_DOMAINS = {
    "gmail.com", "googlemail.com", "outlook.com", "hotmail.com", "live.com",
    "msn.com", "yahoo.com", "ymail.com", "icloud.com", "me.com", "mac.com",
    "aol.com", "proton.me", "protonmail.com", "gmx.com", "zoho.com",
}

# tldextract with the bundled offline snapshot (no network at runtime).
_extract = tldextract.TLDExtract(suffix_list_urls=())


def _domain_of(sender: str) -> str:
    s = sender.strip().lower().strip("<>").strip()
    if "@" in s:
        s = s.rsplit("@", 1)[-1]
    return s.strip()


def sender_domains_to_keywords(senders: list[str]) -> list[str]:
    """Sender emails/domains -> deduped lowercase brand keywords.

    Keyword = registrable domain's second-level label (email.chase.com -> chase).
    Public mailbox providers and malformed inputs are dropped.
    """
    seen, out = set(), []
    for sender in senders:
        domain = _domain_of(sender)
        if not domain:
            continue
        ext = _extract(domain)
        if not ext.domain or not ext.suffix:
            continue  # malformed / no TLD
        if ext.registered_domain in PUBLIC_EMAIL_DOMAINS:
            continue
        kw = ext.domain
        if kw not in seen:
            seen.add(kw)
            out.append(kw)
    return out


def new_brands(found: list[str], existing: list[str]) -> list[str]:
    """Return found keywords not already in existing (case-insensitive, deduped, ordered)."""
    existing_set = {e.strip().lower() for e in existing}
    seen, out = set(), []
    for b in found:
        b2 = b.strip().lower()
        if b2 and b2 not in existing_set and b2 not in seen:
            seen.add(b2)
            out.append(b2)
    return out
