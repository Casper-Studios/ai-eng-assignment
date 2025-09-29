import React, { useState } from 'react';
import { Star, MessageCircle, ThumbsUp, ChevronDown, ChevronUp } from 'lucide-react';
import type { FeaturedTweak, ModificationApplied } from '../types/recipe.types';
import { extractModificationKeywords } from '../utils/diffHighlighter';

interface FeaturedTweaksProps {
  tweaks: FeaturedTweak[];
  modifications?: ModificationApplied[];
  title?: string;
}

export const FeaturedTweaks: React.FC<FeaturedTweaksProps> = ({
  tweaks,
  modifications,
  title = "Featured Community Tweaks"
}) => {
  const [expandedTweaks, setExpandedTweaks] = useState<Set<number>>(new Set());

  // Convert modifications to tweak-like format for display, avoiding duplicates
  const modificationTweaks = modifications?.map(mod => ({
    text: mod.source_review.text,
    rating: mod.source_review.rating,
    has_modification: true,
    is_featured: true,
    modification_type: mod.modification_type,
    reasoning: mod.reasoning
  })) || [];

  // Combine and deduplicate based on text content
  const seenTexts = new Set<string>();
  const allTweaks = [
    ...tweaks.filter(tweak => {
      if (seenTexts.has(tweak.text)) return false;
      seenTexts.add(tweak.text);
      return true;
    }),
    ...modificationTweaks.filter(tweak => {
      if (seenTexts.has(tweak.text)) return false;
      seenTexts.add(tweak.text);
      return true;
    })
  ];

  const toggleTweak = (index: number) => {
    const newExpanded = new Set(expandedTweaks);
    if (newExpanded.has(index)) {
      newExpanded.delete(index);
    } else {
      newExpanded.add(index);
    }
    setExpandedTweaks(newExpanded);
  };

  const renderStars = (rating: number) => {
    return [...Array(5)].map((_, i) => (
      <Star
        key={i}
        className={`w-4 h-4 ${
          i < rating ? 'text-yellow-500 fill-current' : 'text-gray-300'
        }`}
      />
    ));
  };

  const getTweakSummary = (text: string): string => {
    // Extract first sentence or first 100 characters
    const firstSentence = text.split('.')[0];
    if (firstSentence.length > 100) {
      return text.substring(0, 97) + '...';
    }
    return firstSentence + (text.includes('.') ? '.' : '');
  };

  const getModificationBadges = (text: string) => {
    const keywords = extractModificationKeywords(text);
    return keywords.slice(0, 3); // Show first 3 modifications
  };

  if (allTweaks.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">{title}</h3>
        <div className="text-center py-8">
          <MessageCircle className="w-12 h-12 text-gray-400 mx-auto mb-3" />
          <p className="text-gray-500">No featured tweaks available for this recipe</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
        <div className="flex items-center space-x-2">
          <ThumbsUp className="w-4 h-4 text-green-600" />
          <span className="text-sm text-gray-600">{allTweaks.length} featured modifications</span>
        </div>
      </div>

      <div className="space-y-4">
        {allTweaks.map((tweak, index) => {
          const isExpanded = expandedTweaks.has(index);
          const summary = getTweakSummary(tweak.text);
          const isLong = tweak.text.length > summary.length;
          const modificationBadges = getModificationBadges(tweak.text);

          return (
            <div
              key={index}
              className="border border-gray-200 rounded-lg p-4 hover:shadow-sm transition-shadow"
            >
              {/* Header */}
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center space-x-2">
                  {renderStars(tweak.rating)}
                  <span className="text-sm font-medium text-gray-700">
                    {tweak.rating}/5 stars
                  </span>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded-full">
                    Featured
                  </span>
                  {isLong && (
                    <button
                      onClick={() => toggleTweak(index)}
                      className="flex items-center space-x-1 text-primary-600 hover:text-primary-700 text-sm"
                    >
                      {isExpanded ? (
                        <>
                          <span>Show less</span>
                          <ChevronUp className="w-4 h-4" />
                        </>
                      ) : (
                        <>
                          <span>Show more</span>
                          <ChevronDown className="w-4 h-4" />
                        </>
                      )}
                    </button>
                  )}
                </div>
              </div>

              {/* Modification badges */}
              {modificationBadges.length > 0 && (
                <div className="flex flex-wrap gap-2 mb-3">
                  {modificationBadges.map((badge, badgeIndex) => {
                    const [type, description] = badge.split(': ');
                    const badgeColor = {
                      addition: 'bg-green-100 text-green-700 border-green-200',
                      substitution: 'bg-yellow-100 text-yellow-700 border-yellow-200',
                      removal: 'bg-red-100 text-red-700 border-red-200',
                      quantity: 'bg-blue-100 text-blue-700 border-blue-200',
                      temperature: 'bg-orange-100 text-orange-700 border-orange-200',
                      timing: 'bg-purple-100 text-purple-700 border-purple-200'
                    }[type] || 'bg-gray-100 text-gray-700 border-gray-200';

                    return (
                      <span
                        key={badgeIndex}
                        className={`px-2 py-1 text-xs rounded-full border ${badgeColor}`}
                      >
                        {type}: {description}
                      </span>
                    );
                  })}
                </div>
              )}

              {/* Content */}
              <div className="text-gray-700">
                <p className="leading-relaxed">
                  {isExpanded ? tweak.text : summary}
                </p>
              </div>

              {/* Footer */}
              <div className="flex items-center justify-between mt-3 pt-3 border-t border-gray-100">
                <div className="flex items-center space-x-4 text-sm text-gray-500">
                  <span>Community verified</span>
                  <span>•</span>
                  <span>High-rated modification</span>
                </div>
                <div className="flex items-center space-x-1 text-sm text-gray-500">
                  <MessageCircle className="w-4 h-4" />
                  <span>Review</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Summary */}
      <div className="mt-6 p-4 bg-gradient-to-r from-primary-50 to-secondary-50 rounded-lg border">
        <div className="flex items-center space-x-3">
          <div className="flex-shrink-0">
            <div className="w-10 h-10 bg-white rounded-full flex items-center justify-center">
              <ThumbsUp className="w-5 h-5 text-primary-600" />
            </div>
          </div>
          <div>
            <h4 className="font-medium text-gray-900">Community Impact</h4>
            <p className="text-sm text-gray-600">
              These {allTweaks.length} featured modifications have been tested and validated by the community,
              with an average rating of{' '}
              <span className="font-medium">
                {allTweaks.length > 0 ? (allTweaks.reduce((sum, tweak) => sum + tweak.rating, 0) / allTweaks.length).toFixed(1) : '0'}/5 stars
              </span>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};