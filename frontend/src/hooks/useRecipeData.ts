import { useState, useEffect } from 'react';
import type {
  EnhancedRecipe,
  EnhancementReport,
  ValidationMetrics
} from '../types/recipe.types';
import {
  loadAllRecipes,
  loadEnhancementReport,
  filterRecipes,
  sortRecipes
} from '../utils/recipeParser';
import { loadValidationResults } from '../utils/validationMetrics';

export const useRecipeData = () => {
  const [recipes, setRecipes] = useState<EnhancedRecipe[]>([]);
  const [filteredRecipes, setFilteredRecipes] = useState<EnhancedRecipe[]>([]);
  const [enhancementReport, setEnhancementReport] = useState<EnhancementReport | null>(null);
  const [validationMetrics, setValidationMetrics] = useState<ValidationMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filter and sort state
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState<string | null>(null);
  const [minRating, setMinRating] = useState(0);
  const [sortBy, setSortBy] = useState<'title' | 'rating' | 'modifications' | 'date'>('rating');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');

  // Load initial data
  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        setError(null);

        const [recipesData, reportData, validationData] = await Promise.all([
          loadAllRecipes(),
          loadEnhancementReport().catch(() => null),
          loadValidationResults().catch(() => null)
        ]);

        setRecipes(recipesData);
        setEnhancementReport(reportData);
        setValidationMetrics(validationData);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load recipe data');
        console.error('Error loading recipe data:', err);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  // Apply filters and sorting
  useEffect(() => {
    if (recipes.length === 0) return;

    let filtered = filterRecipes(recipes, searchTerm, categoryFilter, minRating);
    filtered = sortRecipes(filtered, sortBy, sortOrder);

    setFilteredRecipes(filtered);
  }, [recipes, searchTerm, categoryFilter, minRating, sortBy, sortOrder]);

  // Get unique categories - fallback to modification types if no categories
  const categories = recipes.reduce<string[]>((acc, recipe) => {
    if (recipe.categories && Array.isArray(recipe.categories)) {
      recipe.categories.forEach(category => {
        if (!acc.includes(category)) {
          acc.push(category);
        }
      });
    } else if (recipe.enhancement_summary?.change_types) {
      // Use enhancement types as categories if no categories exist
      recipe.enhancement_summary.change_types.forEach(type => {
        const category = type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
        if (!acc.includes(category)) {
          acc.push(category);
        }
      });
    }
    return acc;
  }, []);

  // Filter functions
  const updateSearchTerm = (term: string) => {
    setSearchTerm(term);
  };

  const updateCategoryFilter = (category: string | null) => {
    setCategoryFilter(category);
  };

  const updateMinRating = (rating: number) => {
    setMinRating(rating);
  };

  const updateSorting = (
    by: 'title' | 'rating' | 'modifications' | 'date',
    order: 'asc' | 'desc' = 'desc'
  ) => {
    setSortBy(by);
    setSortOrder(order);
  };

  const clearFilters = () => {
    setSearchTerm('');
    setCategoryFilter(null);
    setMinRating(0);
    setSortBy('rating');
    setSortOrder('desc');
  };

  return {
    // Data
    recipes: filteredRecipes,
    allRecipes: recipes,
    enhancementReport,
    validationMetrics,
    categories,

    // State
    loading,
    error,

    // Filters
    searchTerm,
    categoryFilter,
    minRating,
    sortBy,
    sortOrder,

    // Filter functions
    updateSearchTerm,
    updateCategoryFilter,
    updateMinRating,
    updateSorting,
    clearFilters,

    // Stats
    totalRecipes: recipes.length,
    filteredCount: filteredRecipes.length
  };
};