"""Shared helper: keep the pillar back-link block (written by build_pillars.py) when other generators rebuild a page."""
import re

START, END = "<!--pillar-back:start-->", "<!--pillar-back:end-->"
_RX = re.compile(re.escape(START) + ".*?" + re.escape(END), re.S)


def insert(html_, block):
    """Put block (already wrapped in markers) into html_, replacing any existing one."""
    if START in html_:
        return _RX.sub(lambda _: block, html_)
    for anchor in ("</main>", "</article>", "<footer"):
        i = html_.find(anchor) if anchor == "<footer" else html_.rfind(anchor)
        if i > 0:
            return html_[:i] + block + html_[i:]
    raise ValueError("no anchor for pillar back-link")


def carry(out_path, html_):
    """If the file on disk already carries a pillar back-link, keep it in the freshly generated html_."""
    try:
        cur = out_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return html_
    m = _RX.search(cur)
    return insert(html_, m.group(0)) if m else html_


HSTART, HEND = "<!--hreflang:start-->", "<!--hreflang:end-->"
_HRX = re.compile(re.escape(HSTART) + ".*?" + re.escape(HEND), re.S)


def insert_head(html_, block):
    """Put an hreflang block (wrapped in HSTART/HEND) right before </head>, replacing any existing one."""
    if HSTART in html_:
        return _HRX.sub(lambda _: block, html_)
    i = html_.find("</head>")
    if i < 0:
        raise ValueError("no </head>")
    return html_[:i] + block + html_[i:]


_carry_back = carry


def carry(out_path, html_):  # noqa: F811  (extends the back-link carry with the hreflang block)
    html_ = _carry_back(out_path, html_)
    try:
        cur = out_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return html_
    m = _HRX.search(cur)
    return insert_head(html_, m.group(0)) if m else html_
