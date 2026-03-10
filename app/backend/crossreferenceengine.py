import requests
import feedparser
import numpy as np
import re
import time
from urllib.parse import urlparse, quote
from concurrent.futures import ThreadPoolExecutor, as_completed
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from sentence_transformers import SentenceTransformer


TRUSTED_SOURCES = {
    "reuters.com":                    {"name": "Reuters",              "credibility": 1.00, "bias": "center",      "tier": 1, "lang": "en", "region": "international"},
    "apnews.com":                     {"name": "Associated Press",     "credibility": 1.00, "bias": "center",      "tier": 1, "lang": "en", "region": "international"},
    "ptinews.com":                    {"name": "PTI",                  "credibility": 0.95, "bias": "center",      "tier": 1, "lang": "en", "region": "south-asia"},

    "kathmandupost.com":              {"name": "The Kathmandu Post",   "credibility": 0.92, "bias": "center-left", "tier": 2, "lang": "en", "region": "nepal"},
    "myrepublica.com":                {"name": "Republica",            "credibility": 0.90, "bias": "center",      "tier": 2, "lang": "en", "region": "nepal"},
    "therisingnepal.org.np":          {"name": "The Rising Nepal",     "credibility": 0.88, "bias": "center",      "tier": 2, "lang": "en", "region": "nepal"},
    "nepalitimes.com":                {"name": "Nepali Times",         "credibility": 0.92, "bias": "center-left", "tier": 2, "lang": "en", "region": "nepal"},
    "himalmag.com":                   {"name": "Himal Southasian",     "credibility": 0.90, "bias": "center-left", "tier": 2, "lang": "en", "region": "south-asia"},

    "onlinekhabar.com":               {"name": "Online Khabar",        "credibility": 0.85, "bias": "center",      "tier": 3, "lang": "ne", "region": "nepal"},
    "setopati.com":                   {"name": "Setopati",             "credibility": 0.85, "bias": "center",      "tier": 3, "lang": "ne", "region": "nepal"},
    "ratopati.com":                   {"name": "Ratopati",             "credibility": 0.80, "bias": "center",      "tier": 3, "lang": "ne", "region": "nepal"},
    "nepalnews.com":                  {"name": "Nepal News",           "credibility": 0.83, "bias": "center",      "tier": 3, "lang": "en", "region": "nepal"},
    "ekantipur.com":                  {"name": "eKantipur",            "credibility": 0.85, "bias": "center",      "tier": 3, "lang": "ne", "region": "nepal"},
    "nagariknews.nagariknetwork.com": {"name": "Nagarik News",         "credibility": 0.80, "bias": "center",      "tier": 3, "lang": "ne", "region": "nepal"},
    "pahilopost.com":                 {"name": "Pahilo Post",          "credibility": 0.78, "bias": "center",      "tier": 3, "lang": "ne", "region": "nepal"},
    "nepalpatra.com":                 {"name": "Nepal Patra",          "credibility": 0.78, "bias": "center",      "tier": 3, "lang": "ne", "region": "nepal"},
    "janakpur.com":                   {"name": "Janakpur Online",      "credibility": 0.72, "bias": "center",      "tier": 4, "lang": "ne", "region": "nepal"},

    "bbc.com":                        {"name": "BBC News",             "credibility": 0.95, "bias": "center-left", "tier": 2, "lang": "en", "region": "international"},
    "bbc.co.uk":                      {"name": "BBC News",             "credibility": 0.95, "bias": "center-left", "tier": 2, "lang": "en", "region": "international"},
    "aljazeera.com":                  {"name": "Al Jazeera",           "credibility": 0.88, "bias": "center",      "tier": 3, "lang": "en", "region": "international"},
    "theguardian.com":                {"name": "The Guardian",         "credibility": 0.88, "bias": "center-left", "tier": 3, "lang": "en", "region": "international"},
    "thehindu.com":                   {"name": "The Hindu",            "credibility": 0.90, "bias": "center-left", "tier": 2, "lang": "en", "region": "south-asia"},
    "hindustantimes.com":             {"name": "Hindustan Times",      "credibility": 0.85, "bias": "center",      "tier": 3, "lang": "en", "region": "south-asia"},
    "ndtv.com":                       {"name": "NDTV",                 "credibility": 0.85, "bias": "center",      "tier": 3, "lang": "en", "region": "south-asia"},
    "timesofindia.indiatimes.com":    {"name": "Times of India",       "credibility": 0.83, "bias": "center",      "tier": 3, "lang": "en", "region": "south-asia"},
    "dawn.com":                       {"name": "Dawn",                 "credibility": 0.87, "bias": "center-left", "tier": 3, "lang": "en", "region": "south-asia"},
    "bdnews24.com":                   {"name": "bdnews24",             "credibility": 0.80, "bias": "center",      "tier": 3, "lang": "en", "region": "south-asia"},
}

RSS_FEEDS = {
    "kathmandu_post": "https://kathmandupost.com/rss",
    "nepali_times":   "https://www.nepalitimes.com/feed/",
    "rising_nepal":   "https://therisingnepal.org.np/rss",
    "nepalnews":      "https://www.nepalnews.com/feed/",
    "online_khabar":  "https://www.onlinekhabar.com/feed",
    "setopati":       "https://www.setopati.com/feed",
    "ratopati":       "https://ratopati.com/feed",
    "ekantipur":      "https://ekantipur.com/feed",
    "the_hindu":      "https://www.thehindu.com/news/international/rss/",
    "bbc_south_asia": "http://feeds.bbci.co.uk/news/world/south_asia/rss.xml",
    "reuters_asia":   "https://feeds.reuters.com/reuters/INtopNews",
}

WEIGHTS = {
    "semantic_similarity": 0.30,
    "source_credibility":  0.25,
    "date_consistency":    0.20,
    "context_consistency": 0.15,
    "coverage":            0.10,
}


class CrossReferenceEngine:

    def __init__(self):
        print("Loading sentence-transformer model (MiniLM-L6-v2)...")
        self.similarity_model   = SentenceTransformer("all-MiniLM-L6-v2")
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        print("Nepal CrossReferenceEngine ready.")

    def extract_entities(self, text: str) -> dict:
        entities, locations = [], []
        try:
            import spacy
            nlp = spacy.load("en_core_web_sm")
            doc = nlp(text[:4000])
            entities  = list({e.text for e in doc.ents if e.label_ in ["PERSON", "ORG", "EVENT"]})
            locations = list({e.text for e in doc.ents if e.label_ in ["GPE", "LOC"]})
        except Exception:
            words = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
            entities = list(set(words[:10]))
        return {"entities": entities, "locations": locations, "text": text}

    def compute_similarity(self, text_a: str, text_b: str) -> float:
        try:
            emb = self.similarity_model.encode([text_a[:512], text_b[:512]])
            sim = np.dot(emb[0], emb[1]) / (np.linalg.norm(emb[0]) * np.linalg.norm(emb[1]) + 1e-8)
            return float(np.clip(sim, 0.0, 1.0))
        except Exception:
            return 0.5

    def fetch_google_news_nepal(self, query: str) -> list:
        all_articles = []
        for q in [query, f"{query} Nepal"]:
            try:
                encoded = quote(q[:80])
                url = f"https://news.google.com/rss/search?q={encoded}&hl=en-NP&gl=NP&ceid=NP:en"
                resp = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
                feed = feedparser.parse(resp.text)
                for entry in feed.entries[:15]:
                    domain = urlparse(entry.get("link", "")).netloc.replace("www.", "")
                    src = TRUSTED_SOURCES.get(domain, {
                        "name": domain or "Unknown", "credibility": 0.50,
                        "bias": "unknown", "tier": 5, "lang": "en",
                    })
                    all_articles.append({
                        "title":       entry.get("title", ""),
                        "content":     entry.get("summary", entry.get("title", "")),
                        "source":      src["name"],
                        "domain":      domain,
                        "credibility": src["credibility"],
                        "bias":        src.get("bias", "unknown"),
                        "tier":        src.get("tier", 5),
                        "lang":        src.get("lang", "en"),
                        "url":         entry.get("link", ""),
                        "fetch_type":  "google_news_rss_nepal",
                    })
            except Exception as e:
                print(f"  Google News Nepal RSS ({q[:30]}...) failed: {e}")
        return all_articles

    def fetch_single_rss(self, source_key: str, rss_url: str) -> list:
        KEY_TO_DOMAIN = {
            "kathmandu_post": "kathmandupost.com",
            "nepali_times":   "nepalitimes.com",
            "rising_nepal":   "therisingnepal.org.np",
            "nepalnews":      "nepalnews.com",
            "online_khabar":  "onlinekhabar.com",
            "setopati":       "setopati.com",
            "ratopati":       "ratopati.com",
            "ekantipur":      "ekantipur.com",
            "the_hindu":      "thehindu.com",
            "bbc_south_asia": "bbc.com",
            "reuters_asia":   "reuters.com",
        }
        try:
            resp   = requests.get(rss_url, timeout=8, headers={"User-Agent": "Mozilla/5.0"})
            feed   = feedparser.parse(resp.text)
            domain = KEY_TO_DOMAIN.get(source_key, urlparse(rss_url).netloc.replace("www.", ""))
            src    = TRUSTED_SOURCES.get(domain, {
                "name": source_key, "credibility": 0.75, "bias": "center", "tier": 3, "lang": "en",
            })
            articles = []
            for entry in feed.entries[:15]:
                articles.append({
                    "title":       entry.get("title", ""),
                    "content":     entry.get("summary", entry.get("title", "")),
                    "source":      src["name"],
                    "domain":      domain,
                    "credibility": src["credibility"],
                    "bias":        src.get("bias", "center"),
                    "tier":        src.get("tier", 3),
                    "lang":        src.get("lang", "ne"),
                    "url":         entry.get("link", ""),
                    "fetch_type":  "nepal_rss",
                })
            return articles
        except Exception:
            return []

    def fetch_all_nepal_rss(self) -> list:
        results = []
        with ThreadPoolExecutor(max_workers=8) as executor:
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

    def context_consistency(self, orig_info: dict, ref_text: str) -> float:
        ref_info = self.extract_entities(ref_text)
        score, n = 0.0, 0

        orig_e = set(e.lower() for e in orig_info.get("entities", []))
        ref_e  = set(e.lower() for e in ref_info.get("entities",  []))
        if orig_e and ref_e:
            score += len(orig_e & ref_e) / len(orig_e | ref_e)
            n += 1

        orig_l = set(l.lower() for l in orig_info.get("locations", []))
        ref_l  = set(l.lower() for l in ref_info.get("locations",  []))
        if orig_l and ref_l:
            score += len(orig_l & ref_l) / len(orig_l | ref_l)
            n += 1

        s1 = self.sentiment_analyzer.polarity_scores(orig_info.get("text", ""))["compound"]
        s2 = self.sentiment_analyzer.polarity_scores(ref_text)["compound"]
        score += 1.0 - abs(s1 - s2)
        n += 1

        return round(score / n, 4) if n > 0 else 0.5

    def analyze(self, title: str, content: str) -> dict:
        start     = time.time()
        full_text = f"{title} {content}"
        orig_info = self.extract_entities(full_text)
        query     = title.strip() if title.strip() else " ".join(orig_info["entities"][:5])

        with ThreadPoolExecutor(max_workers=2) as ex:
            f_gnews = ex.submit(self.fetch_google_news_nepal, query)
            f_rss   = ex.submit(self.fetch_all_nepal_rss)
            gnews   = f_gnews.result()
            rss     = f_rss.result()

        all_refs = gnews + rss

        matching, contradicting                 = [], []
        similarities, credibilities, ctx_scores = [], [], []

        for ref in all_refs:
            ref_text = f"{ref['title']} {ref['content']}"
            if not ref_text.strip():
                continue

            sim  = self.compute_similarity(full_text[:600], ref_text)
            ctx  = self.context_consistency(orig_info, ref_text)
            cred = ref["credibility"]

            similarities.append(sim)
            credibilities.append(cred)
            ctx_scores.append(ctx)

            entry = {
                "source":      ref["source"],
                "domain":      ref["domain"],
                "title":       ref["title"][:120],
                "url":         ref["url"],
                "similarity":  round(sim,  3),
                "credibility": cred,
                "bias":        ref.get("bias",       "unknown"),
                "tier":        ref.get("tier",       5),
                "lang":        ref.get("lang",       "en"),
                "fetch_type":  ref.get("fetch_type", ""),
            }

            if sim >= 0.55:
                matching.append(entry)
            elif sim < 0.25 and cred >= 0.80:
                contradicting.append(entry)

        matching.sort(     key=lambda x: x["credibility"] * x["similarity"], reverse=True)
        contradicting.sort(key=lambda x: x["credibility"],                    reverse=True)

        sem_sim   = float(np.mean(similarities))  if similarities  else 0.50
        src_cred  = float(np.mean(credibilities)) if credibilities else 0.50
        ctx_cons  = float(np.mean(ctx_scores))    if ctx_scores    else 0.50
        coverage  = min(1.0, len(matching) / 3.0)
        date_cons = 0.70

        raw = (
            WEIGHTS["semantic_similarity"] * sem_sim   +
            WEIGHTS["source_credibility"]  * src_cred  +
            WEIGHTS["date_consistency"]    * date_cons +
            WEIGHTS["context_consistency"] * ctx_cons  +
            WEIGHTS["coverage"]            * coverage
        )
        penalty     = min(0.30, len(contradicting) * 0.10)
        final_score = float(np.clip(raw - penalty, 0.0, 1.0))

        if   final_score >= 0.75: verdict = "LIKELY TRUE"
        elif final_score >= 0.55: verdict = "MOSTLY TRUE"
        elif final_score >= 0.45: verdict = "UNCERTAIN"
        elif final_score >= 0.30: verdict = "MOSTLY FALSE"
        else:                     verdict = "LIKELY FALSE"

        red_flags, green_flags = [], []
        nepal_sources_found    = [m for m in matching if m.get("fetch_type") == "nepal_rss"]

        if len(matching) == 0:
            red_flags.append("No corroborating sources found — story may be fabricated or very niche")
        if contradicting:
            red_flags.append(f"Contradicted by {len(contradicting)} high-credibility source(s)")
        if sem_sim < 0.30:
            red_flags.append(f"Very low semantic similarity to trusted sources ({sem_sim*100:.0f}%)")
        if src_cred < 0.60:
            red_flags.append("Matching sources have low credibility scores")
        if not nepal_sources_found and matching:
            red_flags.append("No Nepal-specific sources corroborate this story")

        if matching:
            green_flags.append(f"Corroborated by {len(matching)} source(s)")
        if nepal_sources_found:
            green_flags.append(f"{len(nepal_sources_found)} Nepal-based source(s) confirm the story")
        if sem_sim >= 0.55:
            green_flags.append(f"High semantic similarity ({sem_sim*100:.0f}%) to trusted reporting")
        if src_cred >= 0.85:
            green_flags.append(f"High-credibility Nepal sources involved (avg {src_cred*100:.0f}%)")

        elapsed = round(time.time() - start, 2)

        return {
            "verdict":           verdict,
            "final_score":       round(final_score, 4),
            "processing_time_s": elapsed,
            "scores": {
                "semantic_similarity": round(sem_sim,   4),
                "source_credibility":  round(src_cred,  4),
                "date_consistency":    round(date_cons, 4),
                "context_consistency": round(ctx_cons,  4),
                "coverage":            round(coverage,  4),
            },
            "weights":               WEIGHTS,
            "sources_checked":       len(all_refs),
            "matching_sources":      matching[:8],
            "contradicting_sources": contradicting[:4],
            "nepal_sources_count":   len(nepal_sources_found),
            "extracted_entities": {
                "people_and_orgs": orig_info["entities"][:10],
                "locations":       orig_info["locations"][:10],
            },
            "red_flags":   red_flags,
            "green_flags": green_flags,
            "score_breakdown": [
                {"factor": "Semantic Similarity", "score": round(sem_sim,   4), "weight": WEIGHTS["semantic_similarity"], "contribution": round(sem_sim   * WEIGHTS["semantic_similarity"], 4)},
                {"factor": "Source Credibility",  "score": round(src_cred,  4), "weight": WEIGHTS["source_credibility"],  "contribution": round(src_cred  * WEIGHTS["source_credibility"],  4)},
                {"factor": "Date Consistency",    "score": round(date_cons, 4), "weight": WEIGHTS["date_consistency"],    "contribution": round(date_cons * WEIGHTS["date_consistency"],    4)},
                {"factor": "Context Consistency", "score": round(ctx_cons,  4), "weight": WEIGHTS["context_consistency"], "contribution": round(ctx_cons  * WEIGHTS["context_consistency"], 4)},
                {"factor": "Coverage",            "score": round(coverage,  4), "weight": WEIGHTS["coverage"],            "contribution": round(coverage  * WEIGHTS["coverage"],            4)},
            ],
        }