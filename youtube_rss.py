from typing import List, Tuple
import feedparser

def channel_feed_url(channel_id: str) -> str:
    return f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"

def parse_entries(feed_url: str) -> List[Tuple[str, str, str]]:
    d = feedparser.parse(feed_url)
    out: List[Tuple[str, str, str]] = []
    for e in getattr(d, "entries", []):
        vid = getattr(e, "yt_videoid", None) or getattr(e, "id", None) or getattr(e, "guid", None)
        link = getattr(e, "link", None) or ""
        title = getattr(e, "title", None) or ""
        if not vid:
            vid = link or title
        out.append((str(vid), str(title), str(link)))
    return out
