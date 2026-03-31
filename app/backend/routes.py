from flask import jsonify, Blueprint, request
from crossreferenceengine import CrossReferenceEngine, TRUSTED_SOURCES

api = Blueprint('api', __name__, url_prefix='/api')

# Create an instance of CrossReferenceEngine (loads the ML model once)
print("Initializing CrossReferenceEngine...")
engine = CrossReferenceEngine()
print("Engine ready!")

# ============ NEW WEIGHTS STRUCTURE FOR NEW SCORING SYSTEM ============
NEW_WEIGHTS = {
    "base_credibility": 0.40,
    "similarity_boost": 0.25,
    "coverage_boost": {
        "15_plus_sources": 0.30,
        "10_plus_sources": 0.25,
        "7_plus_sources": 0.20,
        "5_plus_sources": 0.15,
        "3_plus_sources": 0.10,
        "2_sources": 0.05,
        "1_source": 0.0,
    },
    "tier1_multiplier": {
        "3_plus_sources": 1.30,
        "2_sources": 1.20,
        "1_source": 1.10,
        "0_sources": 1.0,
    }
}

# ============ VERDICT THRESHOLDS ============
VERDICT_THRESHOLDS = {
    "LIKELY_TRUE": 0.80,
    "MOSTLY_TRUE": 0.65,
    "MIXED": 0.45,
    "QUESTIONABLE": 0.25,
}


@api.route('/')
@api.route('/home')
def home():
    return jsonify({
        'message': 'Home Page For NirikshanAI'
    })


@api.route('/about')
def about():
    return jsonify({
        'message': 'NirikshanAI is a project built for Foundation of Data Science'
    })


@api.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'message': 'The NirikshanAI API is working perfectly',
    })


@api.route('/analyze', methods=['POST'])
def analyze():
    """
    Analyze a claim/news and return verification score
    
    Expected JSON:
    {
        "title": "Claim title",
        "content": "Claim content"
    }
    """
    data = request.get_json()
    if not data:
        return jsonify({
            'error': 'The requested data should be JSON'
        }), 400
    
    title = data.get("title", "").strip()
    content = data.get("content", "").strip()

    if not title and not content:
        return jsonify({
            'error': 'At least one of title or content is required'
        }), 400
    
    if len(content) > 10000:
        content = content[:10000]

    try:
        print(f"\n{'='*60}")
        print(f"📝 ANALYZING: {title[:50]}...")
        print(f"{'='*60}")
        
        result = engine.analyze(title, content)
        
        # Enhanced debug output
        print(f"\n[RESULTS]")
        print(f"  ✅ Sources checked: {result.get('sources_checked', 0)}")
        print(f"  ✅ Matching sources: {result.get('scores', {}).get('match_count', 0)}")
        print(f"  ✅ Tier-1 sources: {result.get('tier1_sources_count', 0)}")
        print(f"  ✅ Tier-2 sources: {result.get('tier2_sources_count', 0)}")
        print(f"  ✅ Tier-3 sources: {result.get('tier3_sources_count', 0)}")
        print(f"  ✅ Avg Similarity: {result.get('scores', {}).get('avg_similarity', 0):.3f}")
        print(f"  ✅ Avg Credibility: {result.get('scores', {}).get('avg_credibility', 0):.3f}")
        print(f"  ✅ Final score: {result.get('final_score', 0):.4f}")
        print(f"  ✅ Verdict: {result.get('verdict', 'N/A')}")
        print(f"{'='*60}\n")
        
        return jsonify(result)
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': f'Analysis failed: {str(e)}'
        }), 500


@api.route('/sources', methods=['GET'])
def get_sources():
    """
    Get all trusted sources with their metadata
    """
    sources = [
        {
            'domain': domain,
            'name': info["name"],
            'credibility': info["credibility"],
            'bias': info["bias"],
            'tier': info["tier"],
            'lang': info.get("lang", "en"),
            'region': info.get("region", "unknown")
        } for domain, info in sorted(
            TRUSTED_SOURCES.items(), 
            key=lambda x: (-x[1]["credibility"], x[1]["name"])
        )
    ]

    return jsonify({
        'sources': sources,
        'total': len(sources),
        'by_tier': {
            'tier_1': len([s for s in sources if s['tier'] == 1]),
            'tier_2': len([s for s in sources if s['tier'] == 2]),
            'tier_3': len([s for s in sources if s['tier'] == 3]),
        }
    })


@api.route('/weights', methods=['GET'])
def get_weights():
    """
    Get the NEW SCORING SYSTEM weights and thresholds
    """
    return jsonify({
        'scoring_system': 'NEW - Coverage-Multiplier Based',
        'weights': NEW_WEIGHTS,
        'verdict_thresholds': VERDICT_THRESHOLDS,
        'description': {
            'base_credibility': 'Average credibility of matching sources (40% weight)',
            'similarity_boost': 'Semantic similarity between claim and sources (25% weight)',
            'coverage_boost': 'Exponential boost based on number of sources (25% weight)',
            'tier1_multiplier': 'Multiplicative boost if Tier-1 sources confirm (Reuters, AP, etc.)',
            'final_calculation': '(base + similarity + coverage) × tier1_multiplier'
        }
    })


@api.route('/thresholds', methods=['GET'])
def get_thresholds():
    """
    Get verdict thresholds and scoring ranges
    """
    return jsonify({
        'verdict_ranges': {
            'LIKELY_TRUE': f">= {VERDICT_THRESHOLDS['LIKELY_TRUE']} (80+%)",
            'MOSTLY_TRUE': f"{VERDICT_THRESHOLDS['MOSTLY_TRUE']}-{VERDICT_THRESHOLDS['LIKELY_TRUE']} (65-80%)",
            'MIXED': f"{VERDICT_THRESHOLDS['QUESTIONABLE']}-{VERDICT_THRESHOLDS['MOSTLY_TRUE']} (45-65%)",
            'QUESTIONABLE': f"{VERDICT_THRESHOLDS['QUESTIONABLE']}-{VERDICT_THRESHOLDS['MIXED']} (25-45%)",
            'LIKELY_FALSE': f"< {VERDICT_THRESHOLDS['QUESTIONABLE']} (<25%)",
            'UNVERIFIED': '0.0 (no sources found)',
        },
        'scoring_logic': {
            '0_sources': 'UNVERIFIED (score = 0.0)',
            '1_source': 'Low confidence (no coverage boost)',
            '2_sources': 'Very low confidence (+0.05 coverage)',
            '3_plus_sources': 'Low-medium confidence (+0.10 coverage)',
            '5_plus_sources': 'Medium confidence (+0.15 coverage)',
            '7_plus_sources': 'Good confidence (+0.20 coverage)',
            '10_plus_sources': 'High confidence (+0.25 coverage)',
            '15_plus_sources': 'Very high confidence (+0.30 coverage)',
            'with_tier1_sources': 'Multiplied by 1.10-1.30 depending on count',
        }
    })


@api.route('/explain-score/<float:score>', methods=['GET'])
def explain_score(score):
    """
    Explain what a score means
    """
    if score < 0 or score > 1:
        return jsonify({'error': 'Score must be between 0 and 1'}), 400
    
    if score >= VERDICT_THRESHOLDS['LIKELY_TRUE']:
        verdict = 'LIKELY TRUE'
        explanation = 'Strong evidence from multiple credible sources'
    elif score >= VERDICT_THRESHOLDS['MOSTLY_TRUE']:
        verdict = 'MOSTLY TRUE'
        explanation = 'Good evidence from credible sources'
    elif score >= VERDICT_THRESHOLDS['MIXED']:
        verdict = 'MIXED'
        explanation = 'Some evidence but conflicting or low credibility sources'
    elif score >= VERDICT_THRESHOLDS['QUESTIONABLE']:
        verdict = 'QUESTIONABLE'
        explanation = 'Limited evidence, sources of dubious credibility'
    else:
        verdict = 'LIKELY FALSE'
        explanation = 'Little to no evidence, contradicted by sources'
    
    return jsonify({
        'score': round(score, 4),
        'verdict': verdict,
        'explanation': explanation,
        'confidence_percentage': f'{round(score * 100, 1)}%'
    })