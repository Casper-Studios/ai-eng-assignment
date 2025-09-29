import React, { useState } from 'react';
import { ArrowLeft, Clock, Users, Star, ChevronRight, RotateCcw, Eye, EyeOff } from 'lucide-react';
import type { EnhancedRecipe } from '../types/recipe.types';
import { useComparison } from '../hooks/useComparison';
import {
  formatTime,
  parseTimeToMinutes,
  getRatingNumber
} from '../utils/recipeParser';

interface RecipeComparisonProps {
  enhancedRecipe: EnhancedRecipe;
  onBack?: () => void;
}

export const RecipeComparison: React.FC<RecipeComparisonProps> = ({
  enhancedRecipe,
  onBack
}) => {
  const {
    originalRecipe,
    loading,
    error,
    getTotalChanges,
    getChangeDescription
  } = useComparison(enhancedRecipe);

  const [viewMode, setViewMode] = useState<'side-by-side' | 'enhanced-only' | 'original-only'>('side-by-side');
  const [showFeaturedTweaks, setShowFeaturedTweaks] = useState(false);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-7xl mx-auto">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-200 rounded w-64 mb-6"></div>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <div className="h-96 bg-gray-200 rounded"></div>
              <div className="h-96 bg-gray-200 rounded"></div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error || !originalRecipe) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-600 text-xl font-semibold mb-2">Error Loading Comparison</div>
          <p className="text-gray-600 mb-4">{error || 'Could not load original recipe data'}</p>
          {onBack && (
            <button onClick={onBack} className="btn-primary">
              Back to Dashboard
            </button>
          )}
        </div>
      </div>
    );
  }

  const originalTotalTime = parseTimeToMinutes(originalRecipe.totaltime || '');
  const enhancedTotalTime = parseTimeToMinutes(enhancedRecipe.totaltime || enhancedRecipe.total_time || '');
  const originalRating = getRatingNumber(originalRecipe.rating);
  const enhancedRating = getRatingNumber(enhancedRecipe.rating);

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto p-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-4">
            {onBack && (
              <button
                onClick={onBack}
                className="flex items-center space-x-2 text-gray-600 hover:text-gray-900 transition-colors"
              >
                <ArrowLeft className="w-5 h-5" />
                <span>Back</span>
              </button>
            )}
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{enhancedRecipe.title}</h1>
              <p className="text-gray-600">Original vs Community Enhanced</p>
            </div>
          </div>

          {/* View Mode Toggle */}
          <div className="flex items-center space-x-2 bg-white rounded-lg border p-1">
            <button
              onClick={() => setViewMode('side-by-side')}
              className={`px-3 py-2 rounded text-sm font-medium transition-colors ${
                viewMode === 'side-by-side'
                  ? 'bg-primary-600 text-white'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Side by Side
            </button>
            <button
              onClick={() => setViewMode('enhanced-only')}
              className={`px-3 py-2 rounded text-sm font-medium transition-colors ${
                viewMode === 'enhanced-only'
                  ? 'bg-primary-600 text-white'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Enhanced Only
            </button>
            <button
              onClick={() => setViewMode('original-only')}
              className={`px-3 py-2 rounded text-sm font-medium transition-colors ${
                viewMode === 'original-only'
                  ? 'bg-primary-600 text-white'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Original Only
            </button>
          </div>
        </div>

        {/* Summary */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Enhancement Summary</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Total Changes */}
            <div className="text-center">
              <div className="text-3xl font-bold text-primary-600 mb-2">{getTotalChanges()}</div>
              <div className="text-gray-600">Total Changes</div>
              <div className="text-sm text-gray-500 mt-1">{getChangeDescription()}</div>
            </div>

            {/* Featured Tweaks */}
            <div className="text-center">
              <div className="text-3xl font-bold text-secondary-600 mb-2">
                {enhancedRecipe.featured_tweaks?.length || enhancedRecipe.modifications_applied?.length || 0}
              </div>
              <div className="text-gray-600">Modifications</div>
              <div className="text-sm text-gray-500 mt-1">Community-suggested enhancements</div>
            </div>

            {/* Rating Improvement */}
            <div className="text-center">
              <div className="flex items-center justify-center space-x-2 mb-2">
                <span className="text-lg font-semibold text-gray-600">{originalRating.toFixed(1)}</span>
                <ChevronRight className="w-4 h-4 text-gray-400" />
                <span className="text-3xl font-bold text-green-600">{enhancedRating.toFixed(1)}</span>
              </div>
              <div className="text-gray-600">Rating</div>
              <div className="text-sm text-gray-500 mt-1">
                {enhancedRating > originalRating ? '+' : ''}
                {(enhancedRating - originalRating).toFixed(1)} improvement
              </div>
            </div>
          </div>
        </div>

        {/* Recipe Comparison */}
        <div className={`grid gap-8 ${
          viewMode === 'side-by-side' ? 'grid-cols-1 lg:grid-cols-2' : 'grid-cols-1'
        }`}>
          {/* Original Recipe */}
          {(viewMode === 'side-by-side' || viewMode === 'original-only') && (
            <div className="bg-white rounded-lg shadow-md">
              <div className="bg-secondary-50 px-6 py-4 rounded-t-lg border-b">
                <div className="flex items-center space-x-3">
                  <RotateCcw className="w-5 h-5 text-secondary-600" />
                  <h3 className="text-lg font-semibold text-secondary-800">Original Recipe</h3>
                </div>

                {/* Original Stats */}
                <div className="flex items-center space-x-6 mt-3 text-sm text-secondary-700">
                  <div className="flex items-center space-x-1">
                    <Clock className="w-4 h-4" />
                    <span>{formatTime(originalTotalTime)}</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <Users className="w-4 h-4" />
                    <span>{originalRecipe.servings}</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <Star className="w-4 h-4" />
                    <span>{originalRating.toFixed(1)}</span>
                  </div>
                </div>
              </div>

              <div className="p-6">
                {/* Original Ingredients */}
                <div className="mb-8">
                  <h4 className="font-semibold text-gray-900 mb-3">Ingredients</h4>
                  <ul className="space-y-2">
                    {originalRecipe.ingredients.map((ingredient, index) => (
                      <li key={index} className="text-gray-700 border-l-4 border-gray-200 pl-3">
                        {ingredient}
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Original Instructions */}
                <div>
                  <h4 className="font-semibold text-gray-900 mb-3">Instructions</h4>
                  <ol className="space-y-3">
                    {originalRecipe.instructions.map((instruction, index) => (
                      <li key={index} className="flex">
                        <span className="flex-shrink-0 w-6 h-6 bg-gray-100 text-gray-600 rounded-full flex items-center justify-center text-sm font-medium mr-3 mt-0.5">
                          {index + 1}
                        </span>
                        <span className="text-gray-700">{instruction}</span>
                      </li>
                    ))}
                  </ol>
                </div>
              </div>
            </div>
          )}

          {/* Enhanced Recipe */}
          {(viewMode === 'side-by-side' || viewMode === 'enhanced-only') && (
            <div className="bg-white rounded-lg shadow-md">
              <div className="bg-primary-50 px-6 py-4 rounded-t-lg border-b">
                <div className="flex items-center space-x-3">
                  <Star className="w-5 h-5 text-primary-600 fill-current" />
                  <h3 className="text-lg font-semibold text-primary-800">Enhanced Recipe</h3>
                </div>

                {/* Enhanced Stats */}
                <div className="flex items-center space-x-6 mt-3 text-sm text-primary-700">
                  <div className="flex items-center space-x-1">
                    <Clock className="w-4 h-4" />
                    <span>{formatTime(enhancedTotalTime)}</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <Users className="w-4 h-4" />
                    <span>{enhancedRecipe.servings}</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <Star className="w-4 h-4" />
                    <span>{enhancedRating.toFixed(1)}</span>
                  </div>
                </div>
              </div>

              <div className="p-6">
                {/* Enhanced Ingredients with Featured Tweaks */}
                <div className="mb-8">
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="font-semibold text-gray-900">Ingredients</h4>
                    {(enhancedRecipe.featured_tweaks?.length || enhancedRecipe.modifications_applied?.length) && (
                      <button
                        onClick={() => setShowFeaturedTweaks(!showFeaturedTweaks)}
                        className="flex items-center space-x-2 px-3 py-1 text-sm bg-blue-50 hover:bg-blue-100 text-blue-700 rounded-lg transition-colors"
                      >
                        {showFeaturedTweaks ? (
                          <>
                            <EyeOff className="w-4 h-4" />
                            <span>Hide Modifications</span>
                          </>
                        ) : (
                          <>
                            <Eye className="w-4 h-4" />
                            <span>Show Modifications</span>
                          </>
                        )}
                      </button>
                    )}
                  </div>

                  <div className={`grid gap-6 ${showFeaturedTweaks && (enhancedRecipe.featured_tweaks?.length || enhancedRecipe.modifications_applied?.length) ? 'lg:grid-cols-2' : 'grid-cols-1'}`}>
                    {/* Ingredients List */}
                    <div>
                      <ul className="space-y-2">
                        {enhancedRecipe.ingredients.map((ingredient, index) => {
                          const isNew = !originalRecipe.ingredients.includes(ingredient);
                          return (
                            <li
                              key={index}
                              className={`text-gray-700 border-l-4 pl-3 ${
                                isNew ? 'border-green-400 bg-green-50' : 'border-gray-200'
                              }`}
                            >
                              {ingredient}
                              {isNew && (
                                <span className="ml-2 px-2 py-0.5 bg-green-100 text-green-700 text-xs rounded-full">
                                  New
                                </span>
                              )}
                            </li>
                          );
                        })}
                      </ul>
                    </div>

                    {/* Modifications */}
                    {showFeaturedTweaks && (
                      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                        <h5 className="font-medium text-blue-900 mb-3">
                          {enhancedRecipe.featured_tweaks?.length ? 'Featured Community Tweaks' : 'Applied Modifications'}
                        </h5>
                        <div className="space-y-3">
                          {(enhancedRecipe.featured_tweaks?.length || 0) > 0 ? (
                            enhancedRecipe.featured_tweaks?.map((tweak, index) => (
                              <div key={index} className="bg-white rounded-lg p-3 border border-blue-100">
                                <div className="flex items-start justify-between mb-2">
                                  <div className="flex items-center space-x-2">
                                    {[...Array(5)].map((_, i) => (
                                      <Star
                                        key={i}
                                        className={`w-3 h-3 ${
                                          i < tweak.rating ? 'text-yellow-500 fill-current' : 'text-gray-300'
                                        }`}
                                      />
                                    ))}
                                    <span className="text-xs text-gray-600">{tweak.rating}/5</span>
                                  </div>
                                </div>
                                <p className="text-sm text-gray-700 leading-relaxed">{tweak.text}</p>
                              </div>
                            ))
                          ) : (
                            enhancedRecipe.modifications_applied?.map((modification, index) => (
                              <div key={index} className="bg-white rounded-lg p-3 border border-blue-100">
                                <div className="flex items-start justify-between mb-2">
                                  <div className="flex items-center space-x-2">
                                    {[...Array(5)].map((_, i) => (
                                      <Star
                                        key={i}
                                        className={`w-3 h-3 ${
                                          i < (modification.source_review?.rating || 0) ? 'text-yellow-500 fill-current' : 'text-gray-300'
                                        }`}
                                      />
                                    ))}
                                    <span className="text-xs text-gray-600">{modification.source_review?.rating || 0}/5</span>
                                  </div>
                                  <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded">
                                    {modification.modification_type}
                                  </span>
                                </div>
                                <p className="text-sm text-gray-700 leading-relaxed mb-2">
                                  {modification.source_review?.text}
                                </p>
                                <p className="text-xs text-blue-600 italic">
                                  {modification.reasoning}
                                </p>
                              </div>
                            )) || []
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                </div>

                {/* Enhanced Instructions */}
                <div>
                  <h4 className="font-semibold text-gray-900 mb-3">Instructions</h4>
                  <ol className="space-y-3">
                    {enhancedRecipe.instructions.map((instruction, index) => {
                      const isModified = originalRecipe.instructions[index] !== instruction;
                      return (
                        <li key={index} className="flex">
                          <span className={`flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center text-sm font-medium mr-3 mt-0.5 ${
                            isModified
                              ? 'bg-yellow-100 text-yellow-700'
                              : 'bg-gray-100 text-gray-600'
                          }`}>
                            {index + 1}
                          </span>
                          <span className={`text-gray-700 ${isModified ? 'bg-yellow-50 p-2 rounded' : ''}`}>
                            {instruction}
                            {isModified && (
                              <span className="ml-2 px-2 py-0.5 bg-yellow-100 text-yellow-700 text-xs rounded-full">
                                Modified
                              </span>
                            )}
                          </span>
                        </li>
                      );
                    })}
                  </ol>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};