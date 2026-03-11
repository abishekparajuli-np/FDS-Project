from flask import jsonify, Blueprint, request
from crossreferenceengine import CrossReferenceEngine, TRUSTED_SOURCES, WEIGHTS

api = Blueprint('api', __name__, url_prefix='/api')

# Create an instance of CrossReferenceEngine (loads the ML model once)
print("Initializing CrossReferenceEngine...")
engine = CrossReferenceEngine()
print("Engine ready!")


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
        print(f"\n{'='*50}")
        print(f"📝 Analyzing: {title[:50]}...")
        print(f"{'='*50}")
        
        result = engine.analyze(title, content)
        
        # Debug output
        print(f"✅ Sources checked: {result.get('sources_checked', 0)}")
        print(f"✅ Matching sources: {len(result.get('matching_sources', []))}")
        print(f"✅ Final score: {result.get('final_score', 0)}")
        print(f"✅ Verdict: {result.get('verdict', 'N/A')}")
        print(f"{'='*50}\n")
        
        return jsonify(result)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': str(e)
        }), 500


@api.route('/sources', methods=['GET'])
def get_sources():
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
        'total': len(sources)
    })


@api.route('/weights', methods=['GET'])
def get_weights():
    return jsonify({
        'weights': WEIGHTS
    })