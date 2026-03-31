import requests
import feedparser
import numpy as np
import re
import time
from urllib.parse import urlparse, quote
from concurrent.futures import ThreadPoolExecutor, as_completed
from sentence_transformers import SentenceTransformer


TRUSTED_SOURCES = {
    "reuters.com":       {"name": "Reuters",           "credibility": 0.98, "bias": "center", "tier": 1, "lang": "en", "region": "international"},
    "apnews.com":        {"name": "Associated Press",  "credibility": 0.98, "bias": "center", "tier": 1, "lang": "en", "region": "international"},
    "kathmandupost.com": {"name": "The Kathmandu Post", "credibility": 0.92, "bias": "center-left", "tier": 1, "lang": "en", "region": "nepal"},
    "nepalitimes.com":   {"name": "Nepali Times",       "credibility": 0.90, "bias": "center",      "tier": 1, "lang": "en", "region": "nepal"},
    "myrepublica.com":   {"name": "Republica",          "credibility": 0.88, "bias": "center",      "tier": 1, "lang": "en", "region": "nepal"},
    "bbc.com":           {"name": "BBC News",      "credibility": 0.95, "bias": "center-left", "tier": 2, "lang": "en", "region": "international"},
    "bbc.co.uk":         {"name": "BBC News",      "credibility": 0.95, "bias": "center-left", "tier": 2, "lang": "en", "region": "international"},
    "theguardian.com":   {"name": "The Guardian",  "credibility": 0.88, "bias": "center-left", "tier": 2, "lang": "en", "region": "international"},
    "aljazeera.com":     {"name": "Al Jazeera",    "credibility": 0.85, "bias": "center",      "tier": 2, "lang": "en", "region": "international"},
    "thehindu.com":      {"name": "The Hindu",        "credibility": 0.90, "bias": "center-left", "tier": 2, "lang": "en", "region": "south-asia"},
    "ndtv.com":          {"name": "NDTV",             "credibility": 0.85, "bias": "center",      "tier": 2, "lang": "en", "region": "south-asia"},
    "hindustantimes.com":{"name": "Hindustan Times",  "credibility": 0.83, "bias": "center",      "tier": 2, "lang": "en", "region": "south-asia"},
    "onlinekhabar.com":  {"name": "Online Khabar", "credibility": 0.85, "bias": "center", "tier": 2, "lang": "ne", "region": "nepal"},
    "setopati.com":      {"name": "Setopati",      "credibility": 0.83, "bias": "center", "tier": 2, "lang": "ne", "region": "nepal"},
    "ekantipur.com":     {"name": "eKantipur",     "credibility": 0.85, "bias": "center", "tier": 2, "lang": "ne", "region": "nepal"},
}

RSS_FEEDS = {
    "kathmandu_post": "https://kathmandupost.com/rss",
    "nepali_times":   "https://www.nepalitimes.com/feed/",
    "online_khabar":  "https://www.onlinekhabar.com/feed",
    "setopati":       "https://www.setopati.com/feed",
    "the_hindu":      "https://www.thehindu.com/news/international/rss/",
    "bbc_world":      "http://feeds.bbci.co.uk/news/world/rss.xml",
}

THRESHOLD_LIKELY_TRUE = 0.76
THRESHOLD_MOSTLY_TRUE = 0.60
THRESHOLD_MIXED = 0.50
THRESHOLD_QUESTIONABLE = 0.35


class NewsTextCleaner:
    JUNK_PATTERNS = [
        r'Advertisement\s*\d*', r'Sponsored\s*Content', r'Advertisement\s*',
        r'\(AP\)', r'\(Reuters\)', r'\(AFP\)', r'\(PTI\)', r'\(ANI\)',
        r'File\s*Photo', r'Photo:\s*[\w\s]+', r'Image:\s*[\w\s]+',
        r'Read\s*full\s*story', r'Click\s*here', r'Learn\s*more',
        r'Share\s*this', r'Follow\s*us', r'Subscribe\s*now',
        r'\d{4}-\d{2}-\d{2}', r'\d{2}:\d{2}',
    ]

    @staticmethod
    def clean_text(text: str) -> str:
        if not text:
            return ""
        original_len = len(text)
        text = re.sub(r'<[^>]+>', ' ', text)
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', ' ', text)
        for pattern in NewsTextCleaner.JUNK_PATTERNS:
            text = re.sub(pattern, ' ', text, flags=re.IGNORECASE)
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        text = re.sub(r'\.{3,}', '.', text)
        text = re.sub(r'([a-zA-Z])\1{3,}', r'\1\1', text)
        if len(text.split()) < 3:
            return ""
        cleaned_len = len(text)
        if original_len > 50 and cleaned_len / original_len < 0.3:
            print(f"   Cleaned {original_len}->{cleaned_len} chars ({cleaned_len/original_len:.0%} kept)")
        return text


class CrossReferenceEngine:
    def __init__(self):
        print("Loading CrossReferenceEngine...")
        self.similarity_model = SentenceTransformer("all-MiniLM-L6-v2")
        self.cleaner = NewsTextCleaner()
        print("CrossReferenceEngine loaded successfully")

    def extract_entities(self, text: str) -> dict:
        clean_text = self.cleaner.clean_text(text)
        entities, locations = [], []
        try:
            import spacy
            nlp = spacy.load("en_core_web_sm")
            doc = nlp(clean_text[:4000])
            entities = list({e.text for e in doc.ents if e.label_ in ["PERSON", "ORG", "EVENT"]})
            locations = list({e.text for e in doc.ents if e.label_ in ["GPE", "LOC"]})
        except Exception:
            words = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', clean_text)
            entities = list(set(words[:10]))
        return {"entities": entities, "locations": locations, "text": clean_text}

    def compute_similarity(self, text_a: str, text_b: str) -> float:
        try:
            clean_a = self.cleaner.clean_text(text_a)[:512]
            clean_b = self.cleaner.clean_text(text_b)[:512]
            if not clean_a.strip() or not clean_b.strip():
                return 0.0
            emb = self.similarity_model.encode([clean_a, clean_b])
            sim = np.dot(emb[0], emb[1]) / (np.linalg.norm(emb[0]) * np.linalg.norm(emb[1]) + 1e-8)
            return float(np.clip(sim, 0.0, 1.0))
        except Exception as e:
            print(f"Similarity error: {e}")
            return 0.0

    def fetch_google_news(self, query: str) -> list:
        all_articles = []
        try:
            encoded = quote(query[:80])
            url = f"https://news.google.com/rss/search?q={encoded}&hl=en&gl=US&ceid=US:en"
            resp = requests.get(url, timeout=10, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            })
            feed = feedparser.parse(resp.text)
            
            for entry in feed.entries[:20]:
                link = entry.get("link", "")
                domain = urlparse(link).netloc.replace("www.", "")
                source_info = TRUSTED_SOURCES.get(domain, {
                    "name": domain or "Unknown", "credibility": 0.50,
                    "bias": "unknown", "tier": 3, "lang": "en"
                })
                title = self.cleaner.clean_text(entry.get("title", ""))
                content = self.cleaner.clean_text(entry.get("summary", entry.get("title", "")))
                if not title and not content:
                    continue
                all_articles.append({
                    "title": title,
                    "content": content,
                    "source": source_info["name"],
                    "domain": domain,
                    "credibility": source_info["credibility"],
                    "bias": source_info.get("bias", "unknown"),
                    "tier": source_info.get("tier", 3),
                    "url": link,
                    "fetch_type": "google_news",
                    "raw_title": entry.get("title", ""),
                    "raw_content": entry.get("summary", ""),
                })
        except Exception as e:
            print(f"Error fetching Google News: {e}")
        return all_articles

    def fetch_single_rss(self, source_key: str, rss_url: str) -> list:
        KEY_TO_DOMAIN = {
            "kathmandu_post": "kathmandupost.com", "nepali_times": "nepalitimes.com",
            "online_khabar": "onlinekhabar.com", "setopati": "setopati.com",
            "the_hindu": "thehindu.com", "bbc_world": "bbc.com",
        }
        try:
            resp = requests.get(rss_url, timeout=8, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            })
            feed = feedparser.parse(resp.text)
            
            domain = KEY_TO_DOMAIN.get(source_key, urlparse(rss_url).netloc.replace("www.", ""))
            source_info = TRUSTED_SOURCES.get(domain, {
                "name": source_key, "credibility": 0.70,
                "bias": "center", "tier": 2
            })
            articles = []
            for entry in feed.entries[:10]:
                title = self.cleaner.clean_text(entry.get("title", ""))
                content = self.cleaner.clean_text(entry.get("summary", entry.get("title", "")))
                if not title and not content:
                    continue
                articles.append({
                    "title": title,
                    "content": content,
                    "source": source_info["name"],
                    "domain": domain,
                    "credibility": source_info["credibility"],
                    "bias": source_info.get("bias", "center"),
                    "tier": source_info.get("tier", 2),
                    "url": entry.get("link", ""),
                    "fetch_type": "rss_feed",
                    "raw_title": entry.get("title", ""),
                    "raw_content": entry.get("summary", ""),
                })
            return articles
        except Exception as e:
            print(f"Error fetching RSS {source_key}: {e}")
            return []

    def fetch_all_rss(self) -> list:
        results = []
        with ThreadPoolExecutor(max_workers=6) as executor:
            futures = {
                executor.submit(self.fetch_single_rss, key, url): key
                for key, url in RSS_FEEDS.items()
            }
            for future in as_completed(futures):
                try:
                    results.extend(future.result())
                except Exception:
                    pass
        return results

    def analyze(self, title: str, content: str) -> dict:
        start = time.time()

        clean_title = self.cleaner.clean_text(title)
        clean_content = self.cleaner.clean_text(content)
        full_text = f"{clean_title} {clean_content}"

        orig_info = self.extract_entities(full_text)
        query = clean_title if clean_title.strip() else " ".join(orig_info["entities"][:5])

        with ThreadPoolExecutor(max_workers=2) as ex:
            f_gnews = ex.submit(self.fetch_google_news, query)
            f_rss = ex.submit(self.fetch_all_rss)
            gnews = f_gnews.result()
            rss = f_rss.result()

        all_refs = gnews + rss
        
        if len(all_refs) == 0:
            return self._no_sources_result(orig_info, time.time() - start)

        matching = []
        tier1_matches, tier2_matches, tier3_matches = [], [], []

        for ref in all_refs:
            ref_text = f"{ref['title']} {ref['content']}".strip()
            if not ref_text:
                continue

            sim = self.compute_similarity(full_text[:600], ref_text)

            # QUALITY OVER QUANTITY: Require meaningful semantic match
            if sim < 0.32:
                continue
            # Require at least low-tier credibility (0.40 is tier-3 minimum)
            if ref["credibility"] < 0.42:
                continue

            match_item = {
                "source": ref["source"],
                "domain": ref["domain"],
                "title": ref["title"][:120],
                "url": ref["url"],
                "similarity": round(sim, 3),
                "credibility": ref["credibility"],
                "bias": ref.get("bias", "unknown"),
                "tier": ref.get("tier", 3),
                "fetch_type": ref.get("fetch_type", ""),
            }
            matching.append(match_item)

            if ref.get("tier") == 1:
                tier1_matches.append(ref)
            elif ref.get("tier") == 2:
                tier2_matches.append(ref)
            else:
                tier3_matches.append(ref)



        if len(matching) == 0:
            return self._no_sources_result(orig_info, time.time() - start)

        matching.sort(key=lambda x: x["credibility"] * x["similarity"], reverse=True)

        avg_similarity = float(np.mean([m["similarity"] for m in matching]))
        avg_credibility = float(np.mean([m["credibility"] for m in matching]))
        match_count = len(matching)

        # Balanced scoring: both content matching and source volume matter
        # - Credibility (40%): Source reputation
        # - Similarity (35%): Content matching 
        # - Volume (15%): Multiple sources confirm
        # - Tier-1 (10%): Trusted outlets
        
        # Step 1: Core quality score (credibility + similarity)
        # These are the MAIN factors - they determine if it's true
        core_quality = (avg_credibility * 0.55) + (avg_similarity * 0.45)
        
        # Step 2: Volume confidence (less important but needed)
        # Even low-credibility sources in high volume = story exists
        if match_count >= 25:
            volume_boost = 0.15
        elif match_count >= 15:
            volume_boost = 0.12
        elif match_count >= 10:
            volume_boost = 0.10
        elif match_count >= 7:
            volume_boost = 0.08
        elif match_count >= 5:
            volume_boost = 0.06
        elif match_count >= 3:
            volume_boost = 0.04
        else:
            volume_boost = 0.0

        # Step 3: Tier-1 premium (Reuters, AP, BBC confirm = highest trust)
        tier1_premium = 0.0
        if len(tier1_matches) >= 3:
            tier1_premium = 0.15
        elif len(tier1_matches) == 2:
            tier1_premium = 0.10
        elif len(tier1_matches) == 1:
            tier1_premium = 0.05

        # Final score combines quality and volume equally
        final_score = core_quality + volume_boost + tier1_premium
        final_score = float(np.clip(final_score, 0.0, 1.0))
        quality_factor_used = core_quality

        verdict = self._get_verdict(final_score, match_count)
        red_flags, green_flags = self._generate_flags(
            matching, avg_similarity, avg_credibility, tier1_matches, tier2_matches, tier3_matches, match_count
        )
        elapsed = round(time.time() - start, 2)

        return {
            "verdict": verdict,
            "final_score": round(final_score, 4),
            "processing_time_s": elapsed,
            "data_cleaning_stats": {
                "input_chars_cleaned": len(title + content),
                "input_chars_after": len(full_text),
                "articles_fetched": len(all_refs),
                "articles_matching": len(matching),
            },
            "scores": {
                "avg_similarity": round(avg_similarity, 4),
                "avg_credibility": round(avg_credibility, 4),
                "match_count": match_count,
                "core_quality": round(core_quality, 4),
                "volume_boost": round(volume_boost, 4),
                "tier1_premium": round(tier1_premium, 4),
            },
            "sources_checked": len(all_refs),
            "matching_sources": matching[:10],
            "nepal_sources_count": len([m for m in matching if
                "nepal" in m.get("domain", "").lower() or
                m["source"] in ["The Kathmandu Post", "Nepali Times", "Republica",
                               "Online Khabar", "Setopati", "eKantipur"]]),
            "tier1_sources_count": len(tier1_matches),
            "tier2_sources_count": len(tier2_matches),
            "tier3_sources_count": len(tier3_matches),
            "extracted_entities": {
                "people_and_orgs": orig_info["entities"][:10],
                "locations": orig_info["locations"][:10],
            },
            "red_flags": red_flags,
            "green_flags": green_flags,
            "score_breakdown": [
                {
                    "factor": "Core Quality Score",
                    "value": round(core_quality, 4),
                    "credibility": round(avg_credibility, 3),
                    "similarity": round(avg_similarity, 3),
                    "explanation": "55% source credibility + 45% content match"
                },
                {
                    "factor": "Volume Confirmation",
                    "value": round(volume_boost, 4),
                    "matches": match_count,
                    "explanation": "Multiple sources strengthen confirmation"
                },
                {
                    "factor": "Tier-1 Premium",
                    "value": round(tier1_premium, 4),
                    "tier1_count": len(tier1_matches),
                    "explanation": "Additional confidence from trusted outlets"
                },
                {
                    "factor": "Final Score",
                    "value": round(final_score, 4),
                    "calculation": f"{core_quality:.3f} + {volume_boost:.3f} + {tier1_premium:.3f}",
                    "note": "Balanced: both content match and source volume considered"
                },
            ],
        }

    def _get_verdict(self, score: float, matching_count: int) -> str:
        if matching_count <=0.1:
            return "UNVERIFIED"
        if score >= THRESHOLD_LIKELY_TRUE:
            return "LIKELY TRUE"
        if score >= THRESHOLD_MOSTLY_TRUE:
            return "MOSTLY TRUE"
        if score >= THRESHOLD_MIXED:
            return "MIXED"
        if score >= THRESHOLD_QUESTIONABLE:
            return "QUESTIONABLE"
        return "LIKELY FALSE"

    def _generate_flags(self, matching, avg_sim, avg_cred, tier1_matches, tier2_matches, tier3_matches, match_count) -> tuple:
        red_flags = []
        green_flags = []

        if match_count == 0:
            red_flags.append("No sources found")
        elif match_count == 1:
            red_flags.append("Only 1 source found - insufficient verification")
        elif match_count < 3:
            red_flags.append(f"Low coverage: {match_count} sources found")

        if match_count > 0 and avg_sim < 0.45:
            red_flags.append(f"Low content match ({avg_sim*100:.0f}%)")

        if match_count > 0 and avg_cred < 0.70:
            red_flags.append(f"Source credibility low ({avg_cred*100:.0f}%)")

        if len(tier3_matches) > 2 and len(tier1_matches) == 0:
            red_flags.append("Only low-tier sources")

        if match_count >= 15:
            green_flags.append(f"Excellent coverage: {match_count} sources")
        elif match_count >= 10:
            green_flags.append(f"Strong coverage: {match_count} sources")
        elif match_count >= 5:
            green_flags.append(f"Good coverage: {match_count} sources")
        elif match_count >= 3:
            green_flags.append(f"Multiple sources: {match_count} found")

        if len(tier1_matches) >= 3:
            green_flags.append(f"Multiple tier-1 sources confirm ({len(tier1_matches)} outlets)")
        elif len(tier1_matches) == 2:
            green_flags.append(f"2 tier-1 sources confirm")
        elif len(tier1_matches) == 1:
            green_flags.append(f"Confirmed by tier-1: {tier1_matches[0]['source']}")

        if match_count > 0 and avg_sim >= 0.70:
            green_flags.append(f"High content match ({avg_sim*100:.0f}%)")
        elif match_count > 0 and avg_sim >= 0.55:
            green_flags.append(f"Good content match ({avg_sim*100:.0f}%)")

        if match_count > 0 and avg_cred >= 0.85:
            green_flags.append(f"High credibility sources (avg {avg_cred*100:.0f}%)")
        elif match_count > 0 and avg_cred >= 0.75:
            green_flags.append(f"Credible sources (avg {avg_cred*100:.0f}%)")

        return red_flags, green_flags

    def _no_sources_result(self, orig_info: dict, elapsed: float) -> dict:
        return {
            "verdict": "UNVERIFIED",
            "final_score": 0.0,
            "processing_time_s": round(elapsed, 2),
            "data_cleaning_stats": {"articles_fetched": 0, "articles_matching": 0},
            "scores": {
                "avg_similarity": 0.0,
                "avg_credibility": 0.0,
                "match_count": 0,
                "core_quality": 0.0,
                "volume_boost": 0.0,
                "tier1_premium": 0.0,
            },
            "sources_checked": 0,
            "matching_sources": [],
            "nepal_sources_count": 0,
            "tier1_sources_count": 0,
            "tier2_sources_count": 0,
            "tier3_sources_count": 0,
            "extracted_entities": {
                "people_and_orgs": orig_info["entities"][:10],
                "locations": orig_info["locations"][:10],
            },
            "red_flags": ["No sources found"],
            "green_flags": [],
            "score_breakdown": [],
        }


if __name__ == "__main__":
    engine = CrossReferenceEngine()

    print("\n" + "="*60)
    print("TEST 1: Real news (many credible sources)")
    print("="*60)
    

