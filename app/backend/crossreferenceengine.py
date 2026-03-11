import requests
import feedparser
import numpy as np
import re
import time
from urllib.parse import urlparse, quote
from concurrent.futures import ThreadPoolExecutor, as_completed
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from sentence_transformers import SentenceTransformer


# Only verified, credible sources
TRUSTED_SOURCES = {
    # Tier 1 - Highest Credibility (International Wire Services)
    "reuters.com":       {"name": "Reuters",           "credibility": 0.98, "bias": "center", "tier": 1, "lang": "en", "region": "international"},
    "apnews.com":        {"name": "Associated Press",  "credibility": 0.98, "bias": "center", "tier": 1, "lang": "en", "region": "international"},
    
    # Tier 1 - Nepal's Most Credible English Sources
    "kathmandupost.com": {"name": "The Kathmandu Post", "credibility": 0.92, "bias": "center-left", "tier": 1, "lang": "en", "region": "nepal"},
    "nepalitimes.com":   {"name": "Nepali Times",       "credibility": 0.90, "bias": "center",      "tier": 1, "lang": "en", "region": "nepal"},
    "myrepublica.com":   {"name": "Republica",          "credibility": 0.88, "bias": "center",      "tier": 1, "lang": "en", "region": "nepal"},
    
    # Tier 2 - Credible International Sources
    "bbc.com":           {"name": "BBC News",      "credibility": 0.95, "bias": "center-left", "tier": 2, "lang": "en", "region": "international"},
    "bbc.co.uk":         {"name": "BBC News",      "credibility": 0.95, "bias": "center-left", "tier": 2, "lang": "en", "region": "international"},
    "theguardian.com":   {"name": "The Guardian",  "credibility": 0.88, "bias": "center-left", "tier": 2, "lang": "en", "region": "international"},
    "aljazeera.com":     {"name": "Al Jazeera",    "credibility": 0.85, "bias": "center",      "tier": 2, "lang": "en", "region": "international"},
    
    # Tier 2 - South Asia Credible Sources
    "thehindu.com":      {"name": "The Hindu",        "credibility": 0.90, "bias": "center-left", "tier": 2, "lang": "en", "region": "south-asia"},
    "ndtv.com":          {"name": "NDTV",             "credibility": 0.85, "bias": "center",      "tier": 2, "lang": "en", "region": "south-asia"},
    "hindustantimes.com":{"name": "Hindustan Times",  "credibility": 0.83, "bias": "center",      "tier": 2, "lang": "en", "region": "south-asia"},
    
    # Tier 2 - Nepal Nepali Language Sources (Major)
    "onlinekhabar.com":  {"name": "Online Khabar", "credibility": 0.85, "bias": "center", "tier": 2, "lang": "ne", "region": "nepal"},
    "setopati.com":      {"name": "Setopati",      "credibility": 0.83, "bias": "center", "tier": 2, "lang": "ne", "region": "nepal"},
    "ekantipur.com":     {"name": "eKantipur",     "credibility": 0.85, "bias": "center", "tier": 2, "lang": "ne", "region": "nepal"},
}

# Only reliable RSS feeds
RSS_FEEDS = {
    "kathmandu_post": "https://kathmandupost.com/rss",
    "nepali_times":   "https://www.nepalitimes.com/feed/",
    "online_khabar":  "https://www.onlinekhabar.com/feed",
    "setopati":       "https://www.setopati.com/feed",
    "the_hindu":      "https://www.thehindu.com/news/international/rss/",
    "bbc_world":      "http://feeds.bbci.co.uk/news/world/rss.xml",
}

WEIGHTS = {
    "semantic_similarity": 0.30,
    "source_credibility":  0.25,
    "coverage":            0.25,
    "context_consistency": 0.20,
}


class CrossReferenceEngine:

    def __init__(self):
        print("Loading sentence-transformer model (MiniLM-L6-v2)...")
        self.similarity_model = SentenceTransformer("all-MiniLM-L6-v2")
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        print("CrossReferenceEngine ready.")

    def extract_entities(self, text: str) -> dict:
        entities, locations = [], []
        try:
            import spacy
            nlp = spacy.load("en_core_web_sm")
            doc = nlp(text[:4000])
            entities = list({e.text for e in doc.ents if e.label_ in ["PERSON", "ORG", "EVENT"]})
            locations = list({e.text for e in doc.ents if e.label_ in ["GPE", "LOC"]})
        except Exception:
            # Fallback: extract capitalized words as potential entities
            words = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
            entities = list(set(words[:10]))
        return {"entities": entities, "locations": locations, "text": text}

    def compute_similarity(self, text_a: str, text_b: str) -> float:
        try:
            emb = self.similarity_model.encode([text_a[:512], text_b[:512]])
            sim = np.dot(emb[0], emb[1]) / (np.linalg.norm(emb[0]) * np.linalg.norm(emb[1]) + 1e-8)
            return float(np.clip(sim, 0.0, 1.0))
        except Exception:
            return 0.0

    def fetch_google_news(self, query: str) -> list:
        """Fetch news from Google News RSS"""
        all_articles = []
        try:
            encoded = quote(query[:80])
            url = f"https://news.google.com/rss/search?q={encoded}&hl=en&gl=US&ceid=US:en"
            print(f"  📡 Fetching Google News: {query[:40]}...")
            
            resp = requests.get(url, timeout=10, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            })
            feed = feedparser.parse(resp.text)
            print(f"  ✅ Google News returned {len(feed.entries)} entries")
            
            for entry in feed.entries[:20]:
                # Extract actual source domain from Google News redirect
                link = entry.get("link", "")
                domain = urlparse(link).netloc.replace("www.", "")
                
                # Check if it's from a trusted source
                source_info = TRUSTED_SOURCES.get(domain, {
                    "name": domain or "Unknown",
                    "credibility": 0.50,
                    "bias": "unknown",
                    "tier": 3,
                    "lang": "en",
                })
                
                all_articles.append({
                    "title": entry.get("title", ""),
                    "content": entry.get("summary", entry.get("title", "")),
                    "source": source_info["name"],
                    "domain": domain,
                    "credibility": source_info["credibility"],
                    "bias": source_info.get("bias", "unknown"),
                    "tier": source_info.get("tier", 3),
                    "url": link,
                    "fetch_type": "google_news",
                })
        except Exception as e:
            print(f"  ❌ Google News failed: {e}")
        
        return all_articles

    def fetch_single_rss(self, source_key: str, rss_url: str) -> list:
        """Fetch articles from a single RSS feed"""
        KEY_TO_DOMAIN = {
            "kathmandu_post": "kathmandupost.com",
            "nepali_times": "nepalitimes.com",
            "online_khabar": "onlinekhabar.com",
            "setopati": "setopati.com",
            "the_hindu": "thehindu.com",
            "bbc_world": "bbc.com",
        }
        
        try:
            resp = requests.get(rss_url, timeout=8, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            })
            feed = feedparser.parse(resp.text)
            domain = KEY_TO_DOMAIN.get(source_key, urlparse(rss_url).netloc.replace("www.", ""))
            
            source_info = TRUSTED_SOURCES.get(domain, {
                "name": source_key,
                "credibility": 0.70,
                "bias": "center",
                "tier": 2,
            })
            
            articles = []
            for entry in feed.entries[:10]:
                articles.append({
                    "title": entry.get("title", ""),
                    "content": entry.get("summary", entry.get("title", "")),
                    "source": source_info["name"],
                    "domain": domain,
                    "credibility": source_info["credibility"],
                    "bias": source_info.get("bias", "center"),
                    "tier": source_info.get("tier", 2),
                    "url": entry.get("link", ""),
                    "fetch_type": "rss_feed",
                })
            
            print(f"  ✅ RSS {source_key}: {len(articles)} articles")
            return articles
            
        except Exception as e:
            print(f"  ❌ RSS {source_key} failed: {e}")
            return []

    def fetch_all_rss(self) -> list:
        """Fetch all RSS feeds in parallel"""
        print("  📡 Fetching RSS feeds...")
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
        
        print(f"  📊 Total RSS articles: {len(results)}")
        return results

    def analyze(self, title: str, content: str) -> dict:
        start = time.time()
        full_text = f"{title} {content}"
        orig_info = self.extract_entities(full_text)
        query = title.strip() if title.strip() else " ".join(orig_info["entities"][:5])

        print(f"\n{'='*60}")
        print(f"🔍 Analyzing: {query[:50]}...")
        print(f"{'='*60}")

        # Fetch sources in parallel
        with ThreadPoolExecutor(max_workers=2) as ex:
            f_gnews = ex.submit(self.fetch_google_news, query)
            f_rss = ex.submit(self.fetch_all_rss)
            gnews = f_gnews.result()
            rss = f_rss.result()

        all_refs = gnews + rss
        print(f"\n📊 Total sources fetched: {len(all_refs)}")

        # Handle case when no sources found
        if len(all_refs) == 0:
            return self._no_sources_result(orig_info, time.time() - start)

        # Analyze each reference
        matching = []
        all_similarities = []
        matching_credibilities = []

        print(f"🔄 Computing similarities...")
        
        for ref in all_refs:
            ref_text = f"{ref['title']} {ref['content']}"
            if not ref_text.strip():
                continue

            sim = self.compute_similarity(full_text[:600], ref_text)
            all_similarities.append(sim)

            # Lower threshold for matching (0.40 instead of 0.55)
            if sim >= 0.40:
                matching.append({
                    "source": ref["source"],
                    "domain": ref["domain"],
                    "title": ref["title"][:120],
                    "url": ref["url"],
                    "similarity": round(sim, 3),
                    "credibility": ref["credibility"],
                    "bias": ref.get("bias", "unknown"),
                    "tier": ref.get("tier", 3),
                    "fetch_type": ref.get("fetch_type", ""),
                })
                matching_credibilities.append(ref["credibility"])

        # Sort by combined score
        matching.sort(key=lambda x: x["credibility"] * x["similarity"], reverse=True)

        print(f"✅ Matching sources found: {len(matching)}")

        # Calculate scores based on MATCHING sources only
        if matching:
            avg_similarity = float(np.mean([m["similarity"] for m in matching]))
            avg_credibility = float(np.mean(matching_credibilities))
            coverage = min(1.0, len(matching) / 5.0)  # 5 matching sources = 100% coverage
        else:
            avg_similarity = float(np.max(all_similarities)) if all_similarities else 0.0
            avg_credibility = 0.50
            coverage = 0.0

        # Context consistency (simplified)
        ctx_consistency = min(1.0, len(orig_info["entities"]) / 5.0) * 0.7 + 0.3

        # Calculate final score
        final_score = (
            WEIGHTS["semantic_similarity"] * avg_similarity +
            WEIGHTS["source_credibility"] * avg_credibility +
            WEIGHTS["coverage"] * coverage +
            WEIGHTS["context_consistency"] * ctx_consistency
        )

        # Boost score if we have high-quality matches
        tier1_matches = [m for m in matching if m["tier"] == 1]
        if len(tier1_matches) >= 2:
            final_score = min(1.0, final_score + 0.10)
        elif len(tier1_matches) >= 1:
            final_score = min(1.0, final_score + 0.05)

        # Ensure score is in valid range
        final_score = float(np.clip(final_score, 0.0, 1.0))

        print(f"📈 Avg Similarity: {avg_similarity:.2f}, Avg Credibility: {avg_credibility:.2f}")
        print(f"📈 Coverage: {coverage:.2f}, Final Score: {final_score:.2f}")

        # Determine verdict
        verdict = self._get_verdict(final_score, len(matching))

        # Generate flags
        red_flags, green_flags = self._generate_flags(
            matching, avg_similarity, avg_credibility, tier1_matches
        )

        elapsed = round(time.time() - start, 2)

        return {
            "verdict": verdict,
            "final_score": round(final_score, 4),
            "processing_time_s": elapsed,
            "scores": {
                "semantic_similarity": round(avg_similarity, 4),
                "source_credibility": round(avg_credibility, 4),
                "coverage": round(coverage, 4),
                "context_consistency": round(ctx_consistency, 4),
            },
            "weights": WEIGHTS,
            "sources_checked": len(all_refs),
            "matching_sources": matching[:10],
            "nepal_sources_count": len([m for m in matching if "nepal" in m.get("domain", "").lower() or m["source"] in ["The Kathmandu Post", "Nepali Times", "Republica", "Online Khabar", "Setopati", "eKantipur"]]),
            "tier1_sources_count": len(tier1_matches),
            "extracted_entities": {
                "people_and_orgs": orig_info["entities"][:10],
                "locations": orig_info["locations"][:10],
            },
            "red_flags": red_flags,
            "green_flags": green_flags,
            "score_breakdown": [
                {
                    "factor": "Semantic Similarity",
                    "score": round(avg_similarity, 4),
                    "weight": WEIGHTS["semantic_similarity"],
                    "contribution": round(avg_similarity * WEIGHTS["semantic_similarity"], 4)
                },
                {
                    "factor": "Source Credibility",
                    "score": round(avg_credibility, 4),
                    "weight": WEIGHTS["source_credibility"],
                    "contribution": round(avg_credibility * WEIGHTS["source_credibility"], 4)
                },
                {
                    "factor": "Coverage",
                    "score": round(coverage, 4),
                    "weight": WEIGHTS["coverage"],
                    "contribution": round(coverage * WEIGHTS["coverage"], 4)
                },
                {
                    "factor": "Context Consistency",
                    "score": round(ctx_consistency, 4),
                    "weight": WEIGHTS["context_consistency"],
                    "contribution": round(ctx_consistency * WEIGHTS["context_consistency"], 4)
                },
            ],
        }

    def _get_verdict(self, score: float, matching_count: int) -> str:
        """Determine verdict based on score and matching sources"""
        if matching_count == 0:
            return "UNVERIFIED"
        elif score >= 0.75:
            return "LIKELY TRUE"
        elif score >= 0.60:
            return "MOSTLY TRUE"
        elif score >= 0.45:
            return "MIXED"
        elif score >= 0.30:
            return "QUESTIONABLE"
        else:
            return "LIKELY FALSE"

    def _generate_flags(self, matching, avg_sim, avg_cred, tier1_matches) -> tuple:
        """Generate red and green flags"""
        red_flags = []
        green_flags = []

        # Red flags
        if len(matching) == 0:
            red_flags.append("No corroborating sources found")
        elif len(matching) < 3:
            red_flags.append(f"Only {len(matching)} source(s) corroborate this story")
        
        if avg_sim < 0.50 and matching:
            red_flags.append(f"Low similarity to trusted sources ({avg_sim*100:.0f}%)")
        
        if avg_cred < 0.70 and matching:
            red_flags.append("Matching sources have lower credibility scores")

        # Green flags
        if len(matching) >= 5:
            green_flags.append(f"Strong coverage: {len(matching)} sources corroborate")
        elif len(matching) >= 3:
            green_flags.append(f"Good coverage: {len(matching)} sources corroborate")
        
        if len(tier1_matches) >= 2:
            green_flags.append(f"{len(tier1_matches)} Tier-1 sources (Reuters, AP, major outlets) confirm")
        elif len(tier1_matches) == 1:
            green_flags.append(f"Confirmed by Tier-1 source: {tier1_matches[0]['source']}")
        
        if avg_sim >= 0.70:
            green_flags.append(f"High semantic similarity ({avg_sim*100:.0f}%) to trusted reporting")
        
        if avg_cred >= 0.85:
            green_flags.append(f"High-credibility sources (avg {avg_cred*100:.0f}%)")

        return red_flags, green_flags

    def _no_sources_result(self, orig_info: dict, elapsed: float) -> dict:
        """Return result when no sources could be fetched"""
        return {
            "verdict": "UNABLE TO VERIFY",
            "final_score": 0.50,
            "processing_time_s": round(elapsed, 2),
            "scores": {
                "semantic_similarity": 0.0,
                "source_credibility": 0.0,
                "coverage": 0.0,
                "context_consistency": 0.50,
            },
            "weights": WEIGHTS,
            "sources_checked": 0,
            "matching_sources": [],
            "nepal_sources_count": 0,
            "tier1_sources_count": 0,
            "extracted_entities": {
                "people_and_orgs": orig_info["entities"][:10],
                "locations": orig_info["locations"][:10],
            },
            "red_flags": ["⚠️ Could not fetch news sources - check internet connection"],
            "green_flags": [],
            "score_breakdown": [],
        }