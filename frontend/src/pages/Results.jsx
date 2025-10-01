import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAssessment } from '../context/AssessmentContext';
import { TestLayout } from '../components/assessment/TestLayout';
import api from '../services/api';
import { 
  Loader2, 
  CheckCircle, 
  AlertCircle, 
  TrendingUp, 
  Brain,
  Heart,
  Activity,
  FileText,
  Home
} from 'lucide-react';

export const Results = () => {
  const navigate = useNavigate();
  const { userId, locale, testResults, interactions, resetAssessment } = useAssessment();
  const [loading, setLoading] = useState(true);
  const [report, setReport] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!userId) {
      navigate('/');
      return;
    }

    generateReport();
  }, [userId]);

  const generateReport = async () => {
    setLoading(true);
    try {
      // First submit behavioral data
      if (interactions.length > 0) {
        const interactionSummary = {
          total_interactions: interactions.length,
          tests_completed: Object.keys(testResults).length,
          timestamps: interactions.map(i => i.timestamp),
          actions: interactions.map(i => i.action)
        };

        await api.submitBehavioral({
          user_id: userId,
          interaction_summary: interactionSummary
        });
      }

      // Generate comprehensive report
      const reportData = await api.generateReport({
        user_id: userId,
        locale: locale,
        baseline: null
      });

      setReport(reportData);
    } catch (err) {
      console.error('Report generation failed:', err);
      setError('Failed to generate report. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const getRiskLevelColor = (level) => {
    switch (level?.toLowerCase()) {
      case 'low':
        return 'text-green-600 bg-green-100 border-green-300';
      case 'medium':
        return 'text-yellow-600 bg-yellow-100 border-yellow-300';
      case 'high':
        return 'text-red-600 bg-red-100 border-red-300';
      default:
        return 'text-gray-600 bg-gray-100 border-gray-300';
    }
  };

  const getRiskIcon = (level) => {
    switch (level?.toLowerCase()) {
      case 'low':
        return <CheckCircle className="w-6 h-6" />;
      case 'medium':
      case 'high':
        return <AlertCircle className="w-6 h-6" />;
      default:
        return <Activity className="w-6 h-6" />;
    }
  };

  const handleNewAssessment = () => {
    resetAssessment();
    navigate('/');
  };

  if (loading) {
    return (
      <TestLayout title="Generating Your Report" showBack={false} progress={100}>
        <div className="flex flex-col items-center justify-center py-20 space-y-6">
          <Loader2 className="w-16 h-16 text-blue-600 animate-spin" />
          <p className="text-xl text-gray-700">Analyzing your assessment results...</p>
          <p className="text-sm text-gray-500">This may take a few moments</p>
        </div>
      </TestLayout>
    );
  }

  if (error || !report) {
    return (
      <TestLayout title="Error" showBack={false}>
        <div className="text-center py-20 space-y-6">
          <AlertCircle className="w-16 h-16 text-red-600 mx-auto" />
          <p className="text-xl text-gray-700">{error || 'Failed to load report'}</p>
          <button
            onClick={generateReport}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Try Again
          </button>
        </div>
      </TestLayout>
    );
  }

  const { clinical_report, patient_friendly } = report;

  return (
    <TestLayout 
      title="Your Assessment Results" 
      showBack={false}
      progress={100}
    >
      <div className="space-y-8">
        {/* Overall Risk Score */}
        <div className={`p-6 rounded-lg border-2 ${getRiskLevelColor(clinical_report.risk_level)}`}>
          <div className="flex items-center gap-4">
            {getRiskIcon(clinical_report.risk_level)}
            <div className="flex-1">
              <h3 className="text-2xl font-bold">
                Risk Level: {clinical_report.risk_level?.toUpperCase()}
              </h3>
              <p className="text-sm opacity-80">
                Confidence: {clinical_report.confidence}
              </p>
            </div>
            <div className="text-right">
              <div className="text-4xl font-bold">
                {Math.round(clinical_report.overall_risk_score * 100)}%
              </div>
              <div className="text-sm opacity-80">Risk Score</div>
            </div>
          </div>
        </div>

        {/* Patient-Friendly Summary */}
        <div className="bg-blue-50 p-6 rounded-lg border border-blue-200">
          <div className="flex items-start gap-3">
            <Heart className="w-6 h-6 text-blue-600 flex-shrink-0 mt-1" />
            <div>
              <h3 className="text-xl font-bold text-gray-800 mb-3">
                {patient_friendly.summary}
              </h3>
              <p className="text-gray-700 mb-4">
                {patient_friendly.what_this_means}
              </p>
              <p className="text-gray-600 italic">
                {patient_friendly.reassurance}
              </p>
            </div>
          </div>
        </div>

        {/* Key Findings */}
        <div className="bg-white p-6 rounded-lg border border-gray-200">
          <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
            <Brain className="w-6 h-6 text-purple-600" />
            Key Findings
          </h3>
          <ul className="space-y-2">
            {patient_friendly.key_findings?.map((finding, idx) => (
              <li key={idx} className="flex items-start gap-2">
                <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                <span className="text-gray-700">{finding}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Next Steps */}
        <div className="bg-white p-6 rounded-lg border border-gray-200">
          <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
            <TrendingUp className="w-6 h-6 text-blue-600" />
            Next Steps
          </h3>
          <ul className="space-y-2">
            {patient_friendly.next_steps?.map((step, idx) => (
              <li key={idx} className="flex items-start gap-2">
                <div className="w-6 h-6 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center flex-shrink-0 font-semibold text-sm">
                  {idx + 1}
                </div>
                <span className="text-gray-700">{step}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Clinical Recommendations */}
        {clinical_report.recommendations?.length > 0 && (
          <div className="bg-white p-6 rounded-lg border border-gray-200">
            <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
              <FileText className="w-6 h-6 text-indigo-600" />
              Clinical Recommendations
            </h3>
            <ul className="space-y-2">
              {clinical_report.recommendations.map((rec, idx) => (
                <li key={idx} className="text-gray-700 pl-4 border-l-2 border-indigo-300">
                  {rec}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Red Flags (if any) */}
        {clinical_report.red_flags?.length > 0 && (
          <div className="bg-red-50 p-6 rounded-lg border-2 border-red-200">
            <h3 className="text-xl font-bold text-red-800 mb-4 flex items-center gap-2">
              <AlertCircle className="w-6 h-6" />
              Important Notes
            </h3>
            <ul className="space-y-2">
              {clinical_report.red_flags.map((flag, idx) => (
                <li key={idx} className="text-red-700 font-medium">
                  {flag}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex gap-4 pt-6 border-t border-gray-200">
          <button
            onClick={handleNewAssessment}
            className="flex-1 flex items-center justify-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-all"
            data-testid="new-assessment-btn"
          >
            <Home className="w-5 h-5" />
            Start New Assessment
          </button>
          <button
            onClick={() => window.print()}
            className="px-6 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-all"
          >
            Print Report
          </button>
        </div>

        {/* Disclaimer */}
        <div className="text-xs text-gray-500 text-center p-4 bg-gray-50 rounded-lg">
          <p>
            <strong>Disclaimer:</strong> This assessment provides a risk evaluation and is not a medical diagnosis.
            Please consult with a healthcare professional for proper medical advice and diagnosis.
          </p>
        </div>
      </div>
    </TestLayout>
  );
};