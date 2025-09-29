import React, { useState } from 'react';
import { ArrowLeft, Eye, BarChart3 } from 'lucide-react';
import type { EnhancedRecipe } from '../types/recipe.types';
import { useComparison } from '../hooks/useComparison';
import { RecipeComparison } from '../components/RecipeComparison';
import { ModificationHighlighter } from '../components/ModificationHighlighter';
import { FeaturedTweaks } from '../components/FeaturedTweaks';

interface RecipeDetailProps {
  recipe: EnhancedRecipe;
  onBack?: () => void;
}

export const RecipeDetail: React.FC<RecipeDetailProps> = ({
  recipe,
  onBack
}) => {
  const [activeTab, setActiveTab] = useState<'comparison' | 'modifications' | 'tweaks'>('comparison');

  const {
    ingredientDiffs,
    instructionDiffs,
    changeSummary,
    loading,
    error,
    getTotalChanges
  } = useComparison(recipe);

  const tabs = [
    {
      id: 'comparison' as const,
      label: 'Side-by-Side Comparison',
      icon: Eye,
      description: 'Compare original and enhanced recipes'
    },
    {
      id: 'modifications' as const,
      label: 'Detailed Modifications',
      icon: BarChart3,
      description: 'View ingredient and instruction changes',
      count: getTotalChanges()
    },
    {
      id: 'tweaks' as const,
      label: 'Featured Tweaks',
      icon: BarChart3,
      description: 'Community-verified modifications',
      count: (recipe.featured_tweaks?.length || 0) + (recipe.modifications_applied?.length || 0)
    }
  ];

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
                <span>Back to Dashboard</span>
              </button>
            )}
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{recipe.title}</h1>
              <p className="text-gray-600">Enhanced Recipe Analysis</p>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="bg-white rounded-lg shadow-md mb-8">
          <div className="border-b border-gray-200">
            <nav className="flex space-x-8 px-6">
              {tabs.map((tab) => {
                const Icon = tab.icon;
                const isActive = activeTab === tab.id;

                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`flex items-center space-x-2 py-4 border-b-2 font-medium text-sm transition-colors ${
                      isActive
                        ? 'border-primary-500 text-primary-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                    <span>{tab.label}</span>
                    {tab.count !== undefined && tab.count > 0 && (
                      <span className={`px-2 py-0.5 rounded-full text-xs ${
                        isActive
                          ? 'bg-primary-100 text-primary-700'
                          : 'bg-gray-100 text-gray-600'
                      }`}>
                        {tab.count}
                      </span>
                    )}
                  </button>
                );
              })}
            </nav>
          </div>

          <div className="p-6">
            <div className="text-sm text-gray-600 mb-4">
              {tabs.find(tab => tab.id === activeTab)?.description}
            </div>
          </div>
        </div>

        {/* Tab Content */}
        <div className="space-y-8">
          {activeTab === 'comparison' && (
            <div>
              <RecipeComparison
                enhancedRecipe={recipe}
                onBack={undefined} // We handle back navigation at this level
              />
            </div>
          )}

          {activeTab === 'modifications' && (
            <div className="space-y-8">
              {loading ? (
                <div className="animate-pulse space-y-4">
                  <div className="h-64 bg-gray-200 rounded-lg"></div>
                  <div className="h-64 bg-gray-200 rounded-lg"></div>
                </div>
              ) : error ? (
                <div className="text-center py-12">
                  <div className="text-red-600 text-lg font-semibold mb-2">Error Loading Modifications</div>
                  <p className="text-gray-600">{error}</p>
                </div>
              ) : (
                <>
                  {/* Ingredient Modifications */}
                  <ModificationHighlighter
                    diffs={ingredientDiffs}
                    title="Ingredient Modifications"
                    type="ingredients"
                  />

                  {/* Instruction Modifications */}
                  <ModificationHighlighter
                    diffs={instructionDiffs}
                    title="Instruction Modifications"
                    type="instructions"
                  />

                  {/* Modification Summary */}
                  <div className="bg-white rounded-lg shadow-md p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">
                      Modification Summary
                    </h3>
                    <div className="grid grid-cols-2 md:grid-cols-6 gap-4 text-center">
                      <div className="p-3 bg-green-50 rounded-lg">
                        <div className="text-2xl font-bold text-green-600">
                          {changeSummary.ingredientsAdded}
                        </div>
                        <div className="text-xs text-gray-600">Ingredients Added</div>
                      </div>
                      <div className="p-3 bg-red-50 rounded-lg">
                        <div className="text-2xl font-bold text-red-600">
                          {changeSummary.ingredientsRemoved}
                        </div>
                        <div className="text-xs text-gray-600">Ingredients Removed</div>
                      </div>
                      <div className="p-3 bg-yellow-50 rounded-lg">
                        <div className="text-2xl font-bold text-yellow-600">
                          {changeSummary.ingredientsModified}
                        </div>
                        <div className="text-xs text-gray-600">Ingredients Modified</div>
                      </div>
                      <div className="p-3 bg-green-50 rounded-lg">
                        <div className="text-2xl font-bold text-green-600">
                          {changeSummary.instructionsAdded}
                        </div>
                        <div className="text-xs text-gray-600">Instructions Added</div>
                      </div>
                      <div className="p-3 bg-red-50 rounded-lg">
                        <div className="text-2xl font-bold text-red-600">
                          {changeSummary.instructionsRemoved}
                        </div>
                        <div className="text-xs text-gray-600">Instructions Removed</div>
                      </div>
                      <div className="p-3 bg-yellow-50 rounded-lg">
                        <div className="text-2xl font-bold text-yellow-600">
                          {changeSummary.instructionsModified}
                        </div>
                        <div className="text-xs text-gray-600">Instructions Modified</div>
                      </div>
                    </div>
                  </div>
                </>
              )}
            </div>
          )}

          {activeTab === 'tweaks' && (
            <FeaturedTweaks
              tweaks={recipe.featured_tweaks || []}
              modifications={recipe.modifications_applied}
            />
          )}
        </div>
      </div>
    </div>
  );
};