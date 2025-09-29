import React from 'react';
import { motion } from 'framer-motion';
import { Clock, Users, Star, FileText } from 'lucide-react';
import type { EnhancedRecipe } from '../types/recipe.types';
import {
  formatTime,
  parseTimeToMinutes,
  getRatingNumber,
  getReviewCount
} from '../utils/recipeParser';

interface RecipeCardProps {
  recipe: EnhancedRecipe;
  onSelect?: (recipe: EnhancedRecipe) => void;
  showComparison?: boolean;
}

export const RecipeCard: React.FC<RecipeCardProps> = ({
  recipe,
  onSelect,
  showComparison = false
}) => {
  const handleClick = () => {
    if (onSelect) {
      onSelect(recipe);
    }
  };

  const totalTime = parseTimeToMinutes(recipe.totaltime || recipe.total_time || '');
  const rating = getRatingNumber(recipe.rating) || 0;
  const reviewCount = getReviewCount(recipe.rating) || 0;
  const modificationCount = recipe.modifications_applied?.length ||
                           recipe.reviews?.filter(r => r.has_modification).length || 0;
  const featuredTweaksCount = recipe.featured_tweaks?.length ||
                             recipe.modifications_applied?.filter(m => m.modification_type === 'featured').length || 0;

  return (
    <motion.div
      className={`recipe-card p-6 cursor-pointer ${
        onSelect ? 'hover:shadow-xl' : ''
      }`}
      onClick={handleClick}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ scale: 1.02, y: -5 }}
      whileTap={{ scale: 0.98 }}
      transition={{ duration: 0.2 }}
    >
      {/* Header */}
      <div className="mb-4">
        <h3 className="text-xl font-semibold text-gray-900 mb-2 line-clamp-2">
          {recipe.title}
        </h3>
        <p className="text-gray-600 text-sm line-clamp-3 mb-3">
          {recipe.description}
        </p>

        {/* Categories */}
        {recipe.categories && recipe.categories.length > 0 && (
          <div className="flex flex-wrap gap-2 mb-3">
            {recipe.categories.map((category, index) => (
              <span
                key={index}
                className="px-2 py-1 bg-primary-100 text-primary-700 text-xs rounded-full"
              >
                {category}
              </span>
            ))}
          </div>
        )}

        {/* Enhancement Tags */}
        {modificationCount > 0 && (
          <div className="flex flex-wrap gap-2 mb-3">
            <span className="px-2 py-1 bg-green-100 text-green-700 text-xs rounded-full">
              Enhanced
            </span>
            {recipe.enhancement_summary && (
              <span className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded-full">
                {recipe.enhancement_summary.change_types[0] || 'Modified'}
              </span>
            )}
          </div>
        )}
      </div>

      {/* Stats Row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4 text-sm">
        {/* Rating */}
        <div className="flex items-center space-x-1">
          <Star className="w-4 h-4 text-yellow-500 fill-current" />
          <span className="font-medium">{rating > 0 ? rating.toFixed(1) : 'N/A'}</span>
          {reviewCount > 0 && (
            <span className="text-gray-500">({reviewCount.toLocaleString()})</span>
          )}
        </div>

        {/* Time */}
        <div className="flex items-center space-x-1">
          <Clock className="w-4 h-4 text-gray-500" />
          <span>{totalTime > 0 ? formatTime(totalTime) : 'N/A'}</span>
        </div>

        {/* Servings */}
        <div className="flex items-center space-x-1">
          <Users className="w-4 h-4 text-gray-500" />
          <span>{recipe.servings} servings</span>
        </div>

        {/* Ingredients */}
        <div className="flex items-center space-x-1">
          <FileText className="w-4 h-4 text-gray-500" />
          <span>{recipe.ingredients.length} ingredients</span>
        </div>
      </div>

      {/* Enhancement Stats */}
      <div className="border-t pt-4">
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm font-medium text-gray-700">Community Enhancements</span>
          <div className="flex space-x-2">
            {featuredTweaksCount > 0 && (
              <span className="px-2 py-1 bg-secondary-100 text-secondary-700 text-xs rounded-full">
                {featuredTweaksCount} featured
              </span>
            )}
            {modificationCount > 0 && (
              <span className="px-2 py-1 bg-green-100 text-green-700 text-xs rounded-full">
                {modificationCount} modifications
              </span>
            )}
          </div>
        </div>

        {/* Enhancement Preview */}
        {modificationCount > 0 && recipe.modifications_applied?.[0] ? (
          <div className="bg-gray-50 rounded-lg p-3">
            <p className="text-sm text-gray-600 line-clamp-2">
              {recipe.modifications_applied[0].source_review?.text ||
               recipe.modifications_applied[0].reasoning}
            </p>
            <div className="flex items-center justify-between mt-2">
              <div className="flex items-center space-x-1">
                {[...Array(5)].map((_, i) => (
                  <Star
                    key={i}
                    className={`w-3 h-3 ${
                      i < (recipe.modifications_applied?.[0]?.source_review?.rating || 0)
                        ? 'text-yellow-500 fill-current'
                        : 'text-gray-300'
                    }`}
                  />
                ))}
              </div>
              {modificationCount > 1 && (
                <span className="text-xs text-gray-500">
                  +{modificationCount - 1} more
                </span>
              )}
            </div>
          </div>
        ) : recipe.enhancement_summary ? (
          <div className="bg-blue-50 rounded-lg p-3">
            <p className="text-sm text-blue-600 line-clamp-2">
              {recipe.enhancement_summary.expected_impact}
            </p>
            <div className="mt-2">
              <span className="text-xs text-blue-500">
                {recipe.enhancement_summary.total_changes} enhancement{recipe.enhancement_summary.total_changes !== 1 ? 's' : ''}
              </span>
            </div>
          </div>
        ) : null}

        {/* Comparison Button */}
        {showComparison && (
          <button className="btn-primary w-full mt-3">
            View Comparison
          </button>
        )}
      </div>
    </motion.div>
  );
};