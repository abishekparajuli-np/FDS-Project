from flask import jsonify, Blueprint, request
from crossreferenceengine import CrossReferenceEngine, TRUSTED_SOURCES, WEIGHTS

api = Blueprint('api',__name__,url_prefix='/api')


@api.route('/')
@api.route('/home')
def home():
    return jsonify({
        'message':'Home Page For NirikshanAI'
    })

@api.route('/about')
def about():
    return jsonify({
        'message':'NirikshanAI is a project built for Foundation of Data Science'
    })


@api.route('/health')
def health():
    return jsonify({
        'status':'healthy',
        'message':'The NirikshanAI api is working perfectly',

    })

@api.route('/analyze',methods=['POST'])
def analyze():
    data = request.get_json()
    if not data:
        return jsonify({
            'error':'The requested data should be json'
        })
    title=data.get("title", " ").strip()
    content=data.get("content", " ").strip()

    if not title and not content:
        return jsonify({
            'error':'At least one of title or content is required'
        })
    if len(content) > 10000:
        content= content[:10000]

    try:
        result=CrossReferenceEngine.analyze(title, content)  
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'error':str(e)
        }),500
    return jsonify


@api.route('/sources', methods=['GET'])
def get_sources():
    sources= [
        {
            'domain':domain,
            'name':info["name"],
            'credibility':info["credibility"],
            'bias':info["bias"],
            'tier':info["tier"]
        } for domain , info in sorted(TRUSTED_SOURCES.items(), key=lambda x : (-x[1]["credibility"], x[1]["name"]))
    ]

    return jsonify({
        'sources':sources,
        'total':len(sources)
    })

@api.route('/weights',methods=['GET'])
def weights():
    return jsonify({
        'weights':WEIGHTS
    })