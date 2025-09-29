import React from 'react';
import { CheckCircle, Target, TrendingUp, Shield } from 'lucide-react';
import type { ValidationMetrics, EnhancementReport } from '../types/recipe.types';
import {
  formatValidationScore,
  calculateValidationGrade,
  generateValidationSummary
} from '../utils/validationMetrics';

interface EnhancementMetricsProps {
  validationMetrics: ValidationMetrics | null;
  enhancementReport: EnhancementReport | null;
}

export const EnhancementMetrics: React.FC<EnhancementMetricsProps> = ({
  validationMetrics,
  enhancementReport
}) => {
  if (!validationMetrics || !enhancementReport) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded mb-4"></div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-20 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  const validationSummary = generateValidationSummary(validationMetrics);
  const grade = calculateValidationGrade(validationMetrics);

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-900">Pipeline Validation</h2>
        <div className={`px-4 py-2 rounded-lg font-bold text-2xl ${grade.color} bg-gray-50 border`}>
          Grade: {grade.grade}
        </div>
      </div>

      {/* Grade Description */}
      <div className="mb-6 p-4 bg-gray-50 rounded-lg">
        <p className="text-gray-700">{grade.description}</p>
        <div className="mt-2 flex items-center space-x-4 text-sm text-gray-600">
          <span>{validationSummary.requirementsPassed} of {validationSummary.totalRequirements} requirements passed</span>
          <span className={`px-2 py-1 rounded-full text-xs font-medium ${
            validationSummary.overallStatus === 'pass'
              ? 'bg-green-100 text-green-800'
              : 'bg-red-100 text-red-800'
          }`}>
            {validationSummary.overallStatus.toUpperCase()}
          </span>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
        {/* Multi-modification Accuracy */}
        <div className="text-center">
          <div className="flex items-center justify-center w-12 h-12 bg-primary-100 rounded-lg mx-auto mb-3">
            <Target className="w-6 h-6 text-primary-600" />
          </div>
          <div className="text-2xl font-bold text-gray-900">
            {formatValidationScore(validationMetrics.multi_modification_accuracy)}
          </div>
          <div className="text-sm text-gray-600">Multi-modification</div>
          <div className="text-xs text-gray-500">Target: ≥95%</div>
        </div>

        {/* Recipe Coverage */}
        <div className="text-center">
          <div className="flex items-center justify-center w-12 h-12 bg-secondary-100 rounded-lg mx-auto mb-3">
            <CheckCircle className="w-6 h-6 text-secondary-600" />
          </div>
          <div className="text-2xl font-bold text-gray-900">
            {formatValidationScore(validationMetrics.recipe_coverage)}
          </div>
          <div className="text-sm text-gray-600">Recipe Coverage</div>
          <div className="text-xs text-gray-500">Target: ≥80%</div>
        </div>

        {/* Accuracy Score */}
        <div className="text-center">
          <div className="flex items-center justify-center w-12 h-12 bg-green-100 rounded-lg mx-auto mb-3">
            <TrendingUp className="w-6 h-6 text-green-600" />
          </div>
          <div className="text-2xl font-bold text-gray-900">
            {formatValidationScore(validationMetrics.accuracy_score)}
          </div>
          <div className="text-sm text-gray-600">Accuracy Score</div>
          <div className="text-xs text-gray-500">Target: ≥90%</div>
        </div>

        {/* Safety Score */}
        <div className="text-center">
          <div className="flex items-center justify-center w-12 h-12 bg-blue-100 rounded-lg mx-auto mb-3">
            <Shield className="w-6 h-6 text-blue-600" />
          </div>
          <div className="text-2xl font-bold text-gray-900">
            {formatValidationScore(validationMetrics.safety_score)}
          </div>
          <div className="text-sm text-gray-600">Safety Score</div>
          <div className="text-xs text-gray-500">Target: 100%</div>
        </div>
      </div>

      {/* Enhancement Report */}
      <div className="border-t pt-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Enhancement Report</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div className="text-center p-3 bg-gray-50 rounded-lg">
            <div className="text-xl font-bold text-gray-900">{enhancementReport.total_recipes}</div>
            <div className="text-gray-600">Total Recipes</div>
          </div>
          <div className="text-center p-3 bg-green-50 rounded-lg">
            <div className="text-xl font-bold text-green-600">{enhancementReport.successfully_enhanced}</div>
            <div className="text-gray-600">Enhanced</div>
          </div>
          <div className="text-center p-3 bg-blue-50 rounded-lg">
            <div className="text-xl font-bold text-blue-600">
              {enhancementReport.enhanced_files.reduce((sum, file) => sum + file.modification_reviews, 0)}
            </div>
            <div className="text-gray-600">Modifications</div>
          </div>
          <div className="text-center p-3 bg-yellow-50 rounded-lg">
            <div className="text-xl font-bold text-yellow-600">{enhancementReport.synthetic_reviews_added}</div>
            <div className="text-gray-600">Synthetic Reviews</div>
          </div>
        </div>
      </div>

      {/* Requirements Status */}
      <div className="border-t pt-6 mt-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">PRD Requirements Status</h3>
        <div className="space-y-3">
          {validationSummary.requirements.map((req, index) => (
            <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div className="flex-1">
                <div className="flex items-center space-x-2">
                  <span className={`w-2 h-2 rounded-full ${
                    req.status === 'pass' ? 'bg-green-500' : 'bg-red-500'
                  }`}></span>
                  <span className="font-medium text-gray-900">{req.requirement}</span>
                </div>
                <p className="text-sm text-gray-600 mt-1">{req.description}</p>
              </div>
              <div className="text-right">
                <div className="text-sm font-medium text-gray-900">{req.achieved}</div>
                <div className="text-xs text-gray-500">Target: {req.target}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};