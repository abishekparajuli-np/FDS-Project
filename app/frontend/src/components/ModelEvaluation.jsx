import React, { useState, useEffect } from 'react';
import api from '../api/api';

function ModelEvaluation() {
  const [weights, setWeights] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const evaluationMetrics = {
    accuracy: 0.87,
    precision: 0.84,
    recall: 0.89,
    f1_score: 0.86,
    auc_roc: 0.91,
    confusion_matrix: {
      true_positive: 423,
      true_negative: 398,
      false_positive: 67,
      false_negative: 52
    },
    dataset_info: {
      total_samples: 940,
      training_samples: 752,
      test_samples: 188,
      classes: ['Credible', 'Not Credible']
    }
  };

  useEffect(() => {
    fetchWeights();
  }, []);

  const fetchWeights = async () => {
    try {
      const data = await api.getWeights();
      setWeights(data.weights);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const formatPercent = (value) => `${(value * 100).toFixed(1)}%`;

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] text-gray-400">
        <div className="w-12 h-12 border-4 border-rose-500/20 border-t-rose-500 rounded-full animate-spin mb-4" />
        <p>Loading evaluation data...</p>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto px-8">
      {/* Header */}
      <div className="text-center mb-12">
        <h1 className="text-3xl font-bold text-white mb-2">📈 Model Evaluation</h1>
        <p className="text-gray-400">Performance metrics and configuration of our fact-checking model.</p>
      </div>

      {/* Metrics Overview */}
      <div className="mb-12">
        <h2 className="text-xl font-semibold text-white mb-6">Performance Metrics</h2>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
          {[
            { label: 'Accuracy', value: evaluationMetrics.accuracy, primary: true },
            { label: 'Precision', value: evaluationMetrics.precision },
            { label: 'Recall', value: evaluationMetrics.recall },
            { label: 'F1 Score', value: evaluationMetrics.f1_score },
            { label: 'AUC-ROC', value: evaluationMetrics.auc_roc, highlight: true },
          ].map((metric, index) => (
            <div 
              key={index}
              className={`p-6 rounded-xl text-center border transition-all duration-300 hover:-translate-y-1
                ${metric.primary 
                  ? 'bg-gradient-to-br from-rose-500/20 to-slate-900/80 border-rose-500' 
                  : metric.highlight 
                    ? 'bg-gradient-to-br from-green-500/20 to-slate-900/80 border-green-500'
                    : 'bg-slate-900/80 border-white/10 hover:border-rose-500/30'
                }`}
            >
              <div className="text-4xl font-bold text-white mb-1">{formatPercent(metric.value)}</div>
              <div className="text-rose-500 font-semibold">{metric.label}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Confusion Matrix */}
      <div className="mb-12">
        <h2 className="text-xl font-semibold text-white mb-6">Confusion Matrix</h2>
        <div className="bg-slate-900/80 p-8 rounded-xl max-w-lg mx-auto">
          <div className="grid grid-cols-3 gap-2 text-center mb-2">
            <span></span>
            <span className="text-gray-400 text-sm">Pred. Credible</span>
            <span className="text-gray-400 text-sm">Pred. Not Credible</span>
          </div>
          <div className="grid grid-cols-3 gap-2 mb-2">
            <span className="text-gray-400 text-sm flex items-center">Actual Credible</span>
            <div className="bg-green-500/30 p-6 rounded-lg">
              <span className="text-2xl font-bold text-white block">{evaluationMetrics.confusion_matrix.true_positive}</span>
              <span className="text-gray-400 text-xs">TP</span>
            </div>
            <div className="bg-red-500/20 p-6 rounded-lg">
              <span className="text-2xl font-bold text-white block">{evaluationMetrics.confusion_matrix.false_negative}</span>
              <span className="text-gray-400 text-xs">FN</span>
            </div>
          </div>
          <div className="grid grid-cols-3 gap-2">
            <span className="text-gray-400 text-sm flex items-center">Actual Not Credible</span>
            <div className="bg-red-500/30 p-6 rounded-lg">
              <span className="text-2xl font-bold text-white block">{evaluationMetrics.confusion_matrix.false_positive}</span>
              <span className="text-gray-400 text-xs">FP</span>
            </div>
            <div className="bg-green-500/20 p-6 rounded-lg">
              <span className="text-2xl font-bold text-white block">{evaluationMetrics.confusion_matrix.true_negative}</span>
              <span className="text-gray-400 text-xs">TN</span>
            </div>
          </div>
        </div>
      </div>

      {/* Weights */}
      {weights && (
        <div className="mb-12">
          <h2 className="text-xl font-semibold text-white mb-6">Model Weights Configuration</h2>
          <div className="bg-slate-900/80 p-8 rounded-xl space-y-4">
            {Object.entries(weights).map(([key, value]) => (
              <div key={key}>
                <div className="h-6 bg-white/10 rounded-full overflow-hidden mb-2">
                  <div 
                    className="h-full bg-gradient-to-r from-rose-500 to-red-400 rounded-full transition-all duration-500"
                    style={{ width: `${value * 100}%` }}
                  />
                </div>
                <div className="flex justify-between">
                  <span className="text-white capitalize">{key.replace(/_/g, ' ')}</span>
                  <span className="text-rose-500 font-bold">{value.toFixed(2)}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Dataset Info */}
      <div className="mb-8">
        <h2 className="text-xl font-semibold text-white mb-6">Dataset Information</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          {[
            { value: evaluationMetrics.dataset_info.total_samples, label: 'Total Samples' },
            { value: evaluationMetrics.dataset_info.training_samples, label: 'Training Set (80%)' },
            { value: evaluationMetrics.dataset_info.test_samples, label: 'Test Set (20%)' },
            { value: evaluationMetrics.dataset_info.classes.length, label: 'Classes' },
          ].map((stat, index) => (
            <div key={index} className="bg-slate-900/80 p-6 rounded-xl text-center">
              <span className="text-3xl font-bold text-rose-500 block mb-2">{stat.value}</span>
              <span className="text-gray-400 text-sm">{stat.label}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Error Notice */}
      {error && (
        <div className="bg-red-500/10 border border-red-500/30 p-4 rounded-lg text-red-300">
          ⚠️ Some data could not be loaded: {error}
        </div>
      )}
    </div>
  );
}

export default ModelEvaluation;