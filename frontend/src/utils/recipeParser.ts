import type {
  EnhancedRecipe,
  OriginalRecipe,
  RecipeComparison,
  ModificationDetail,
  EnhancementReport
} from '../types/recipe.types';

/**
 * Parses time string (PT20M format) to minutes
 */
export const parseTimeToMinutes = (timeString: string): number => {
  if (!timeString) return 0;

  const match = timeString.match(/PT(?:(\d+)H)?(?:(\d+)M)?/);
  if (!match) return 0;

  const hours = parseInt(match[1] || '0');
  const minutes = parseInt(match[2] || '0');

  return hours * 60 + minutes;
};

/**
 * Formats minutes to readable time string
 */
export const formatTime = (minutes: number): string => {
  if (minutes < 60) {
    return `${minutes} min`;
  }

  const hours = Math.floor(minutes / 60);
  const remainingMinutes = minutes % 60;

  if (remainingMinutes === 0) {
    return `${hours} hr`;
  }

  return `${hours} hr ${remainingMinutes} min`;
};

/**
 * Extracts rating as number from recipe rating object
 */
export const getRatingNumber = (rating?: { value: string; count: string }): number => {
  if (!rating) return 0;
  return parseFloat(rating.value) || 0;
};

/**
 * Gets review count as number
 */
export const getReviewCount = (rating?: { value: string; count: string }): number => {
  if (!rating) return 0;
  return parseInt(rating.count.replace(/,/g, '')) || 0;
};

/**
 * Loads enhanced recipe data from JSON
 */
export const loadEnhancedRecipe = async (filename: string): Promise<EnhancedRecipe> => {
  try {
    const response = await fetch(`/data/enhanced/${filename}`);
    if (!response.ok) {
      throw new Error(`Failed to load recipe: ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    console.error(`Error loading enhanced recipe ${filename}:`, error);
    throw error;
  }
};

/**
 * Loads original recipe data from JSON
 */
export const loadOriginalRecipe = async (filename: string): Promise<OriginalRecipe> => {
  try {
    const response = await fetch(`/data/${filename}`);
    if (!response.ok) {
      throw new Error(`Failed to load original recipe: ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    console.error(`Error loading original recipe ${filename}:`, error);
    throw error;
  }
};

/**
 * Loads all enhanced recipes
 */
export const loadAllEnhancedRecipes = async (): Promise<EnhancedRecipe[]> => {
  try {
    const enhancementReport = await fetch('/data/enhanced/enhancement_report.json').then(r => r.json()) as EnhancementReport;

    const recipes = await Promise.all(
      enhancementReport.enhanced_files.map(file =>
        loadEnhancedRecipe(file.enhanced_file)
      )
    );

    return recipes;
  } catch (error) {
    console.error('Error loading enhanced recipes:', error);
    throw error;
  }
};

/**
 * Loads all original recipes with featured tweaks
 */
export const loadAllOriginalRecipes = async (): Promise<OriginalRecipe[]> => {
  try {
    // Try to load known recipe files
    const recipeFiles = [
      'recipe_10813_best-chocolate-chip-cookies.json',
      'recipe_77935_creamy-sweet-potato-with-ginger-soup.json',
      'recipe_19117_spicy-apple-cake.json',
      'recipe_144299_nikujaga-japanese-style-meat-and-potatoes-.json',
      'recipe_284494_spiced-purple-plum-jam.json',
      'recipe_45613_mango-teriyaki-marinade.json'
    ];

    const recipes: OriginalRecipe[] = [];

    for (const filename of recipeFiles) {
      try {
        const recipe = await loadOriginalRecipe(filename);
        recipes.push(recipe);
      } catch (error) {
        console.warn(`Could not load ${filename}:`, error);
        // Continue loading other recipes
      }
    }

    return recipes;
  } catch (error) {
    console.error('Error loading original recipes:', error);
    throw error;
  }
};

/**
 * Loads all recipes (both original and enhanced) and creates a unified view
 */
export const loadAllRecipes = async (): Promise<EnhancedRecipe[]> => {
  try {
    const [enhancedRecipes, originalRecipes] = await Promise.all([
      loadAllEnhancedRecipes().catch(() => []),
      loadAllOriginalRecipes().catch(() => [])
    ]);

    // Convert original recipes to enhanced recipe format for unified display
    const convertedOriginals: EnhancedRecipe[] = originalRecipes.map(original => ({
      recipe_id: `${original.recipe_id}_original`,
      original_recipe_id: original.recipe_id,
      title: original.title,
      description: original.description,
      ingredients: original.ingredients,
      instructions: original.instructions,
      modifications_applied: [],
      enhancement_summary: {
        total_changes: 0,
        change_types: [],
        expected_impact: 'Original recipe - no modifications applied'
      },
      servings: original.servings,
      prep_time: original.preptime,
      cook_time: original.cooktime,
      total_time: original.totaltime,
      created_at: original.scraped_at,
      pipeline_version: '1.0.0',

      // Include original recipe data
      url: original.url,
      scraped_at: original.scraped_at,
      rating: original.rating,
      preptime: original.preptime,
      cooktime: original.cooktime,
      totaltime: original.totaltime,
      nutrition: original.nutrition,
      author: original.author,
      categories: original.categories,
      featured_tweaks: original.featured_tweaks,
      reviews: original.reviews
    }));

    // Combine both types, with enhanced recipes taking priority
    const allRecipes = [...enhancedRecipes, ...convertedOriginals];

    // Remove duplicates, preferring enhanced versions
    const recipeMap = new Map<string, EnhancedRecipe>();

    for (const recipe of allRecipes) {
      const baseId = recipe.original_recipe_id || recipe.recipe_id.replace('_enhanced', '').replace('_original', '');

      if (!recipeMap.has(baseId)) {
        recipeMap.set(baseId, recipe);
      } else {
        // Prefer enhanced version over original
        const existing = recipeMap.get(baseId)!;
        if (recipe.recipe_id.includes('_enhanced') && !existing.recipe_id.includes('_enhanced')) {
          recipeMap.set(baseId, recipe);
        }
      }
    }

    return Array.from(recipeMap.values());
  } catch (error) {
    console.error('Error loading all recipes:', error);
    throw error;
  }
};

/**
 * Loads enhancement report
 */
export const loadEnhancementReport = async (): Promise<EnhancementReport> => {
  try {
    const response = await fetch('/data/enhanced/enhancement_report.json');
    if (!response.ok) {
      throw new Error(`Failed to load enhancement report: ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error loading enhancement report:', error);
    throw error;
  }
};

/**
 * Analyzes modifications between original and enhanced recipe
 */
export const analyzeModifications = (
  original: OriginalRecipe,
  enhanced: EnhancedRecipe
): ModificationDetail[] => {
  const modifications: ModificationDetail[] = [];

  // Analyze ingredient changes
  const originalIngredients = new Set(original.ingredients);
  const enhancedIngredients = new Set(enhanced.ingredients);

  // Find added ingredients
  enhanced.ingredients.forEach(ingredient => {
    if (!originalIngredients.has(ingredient)) {
      modifications.push({
        type: 'addition',
        category: 'ingredient',
        modifiedText: ingredient,
        reason: 'Community-suggested ingredient addition',
        source: enhanced.featured_tweaks?.[0] || enhanced.reviews?.[0] || {
          text: 'Community enhancement',
          rating: 5,
          has_modification: true,
          is_featured: true
        }, // Simplified source attribution
        impact: {
          flavor: 'positive',
          texture: 'neutral',
          difficulty: 'same',
          time: 'same'
        }
      });
    }
  });

  // Find removed ingredients
  original.ingredients.forEach(ingredient => {
    if (!enhancedIngredients.has(ingredient)) {
      modifications.push({
        type: 'removal',
        category: 'ingredient',
        originalText: ingredient,
        reason: 'Community-suggested ingredient removal',
        source: enhanced.featured_tweaks?.[0] || enhanced.reviews?.[0] || {
          text: 'Community enhancement',
          rating: 5,
          has_modification: true,
          is_featured: true
        },
        impact: {
          flavor: 'neutral',
          texture: 'neutral',
          difficulty: 'easier',
          time: 'faster'
        }
      });
    }
  });

  // Analyze instruction changes (simplified)
  if (original.instructions.length !== enhanced.instructions.length) {
    modifications.push({
      type: 'modification',
      category: 'instruction',
      originalText: `${original.instructions.length} steps`,
      modifiedText: `${enhanced.instructions.length} steps`,
      reason: 'Community-suggested process modification',
      source: enhanced.featured_tweaks?.[0] || enhanced.reviews?.[0] || {
        text: 'Community enhancement',
        rating: 5,
        has_modification: true,
        is_featured: true
      },
      impact: {
        flavor: 'positive',
        texture: 'positive',
        difficulty: 'same',
        time: 'same'
      }
    });
  }

  return modifications;
};

/**
 * Creates a comparison object between original and enhanced recipe
 */
export const createRecipeComparison = async (
  enhancedFilename: string,
  originalFilename: string
): Promise<RecipeComparison> => {
  try {
    const [enhanced, original] = await Promise.all([
      loadEnhancedRecipe(enhancedFilename),
      loadOriginalRecipe(originalFilename)
    ]);

    const modifications = analyzeModifications(original, enhanced);

    return {
      original,
      enhanced,
      modifications
    };
  } catch (error) {
    console.error('Error creating recipe comparison:', error);
    throw error;
  }
};

/**
 * Calculates recipe statistics
 */
export const calculateRecipeStats = (recipe: EnhancedRecipe) => {
  const totalTime = parseTimeToMinutes(recipe.totaltime || recipe.total_time || '');
  const prepTime = parseTimeToMinutes(recipe.preptime || recipe.prep_time || '');
  const cookTime = parseTimeToMinutes(recipe.cooktime || recipe.cook_time || '');

  // For new enhanced recipe format, use modifications_applied instead of reviews
  const modificationCount = recipe.modifications_applied?.length ||
                          recipe.reviews?.filter(r => r.has_modification).length || 0;
  const featuredTweaksCount = recipe.featured_tweaks?.length || 0;
  const averageRating = getRatingNumber(recipe.rating);
  const reviewCount = getReviewCount(recipe.rating);

  return {
    totalTime,
    prepTime,
    cookTime,
    modificationCount,
    featuredTweaksCount,
    averageRating,
    reviewCount,
    ingredientCount: recipe.ingredients.length,
    instructionCount: recipe.instructions.length,
    categories: recipe.categories || []
  };
};

/**
 * Filters recipes based on criteria
 */
export const filterRecipes = (
  recipes: EnhancedRecipe[],
  searchTerm: string,
  categoryFilter: string | null,
  minRating: number
): EnhancedRecipe[] => {
  return recipes.filter(recipe => {
    // Search term filter
    if (searchTerm) {
      const searchLower = searchTerm.toLowerCase();
      const titleMatch = recipe.title.toLowerCase().includes(searchLower);
      const descriptionMatch = recipe.description.toLowerCase().includes(searchLower);
      const categoryMatch = recipe.categories?.some(cat =>
        cat.toLowerCase().includes(searchLower)
      ) || false;

      if (!titleMatch && !descriptionMatch && !categoryMatch) {
        return false;
      }
    }

    // Category filter - check both categories and enhancement types
    if (categoryFilter) {
      const hasCategory = recipe.categories && recipe.categories.includes(categoryFilter);
      const hasEnhancementType = recipe.enhancement_summary?.change_types.some(type =>
        type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()) === categoryFilter
      );
      if (!hasCategory && !hasEnhancementType) {
        return false;
      }
    }

    // Rating filter
    if (getRatingNumber(recipe.rating) < minRating) {
      return false;
    }

    return true;
  });
};

/**
 * Sorts recipes based on criteria
 */
export const sortRecipes = (
  recipes: EnhancedRecipe[],
  sortBy: 'title' | 'rating' | 'modifications' | 'date',
  sortOrder: 'asc' | 'desc' = 'desc'
): EnhancedRecipe[] => {
  const sorted = [...recipes].sort((a, b) => {
    let comparison = 0;

    switch (sortBy) {
      case 'title':
        comparison = a.title.localeCompare(b.title);
        break;
      case 'rating':
        comparison = getRatingNumber(a.rating) - getRatingNumber(b.rating);
        break;
      case 'modifications': {
        const aModCount = (a.modifications_applied?.length || 0) + (a.featured_tweaks?.length || 0);
        const bModCount = (b.modifications_applied?.length || 0) + (b.featured_tweaks?.length || 0);
        comparison = aModCount - bModCount;
        break;
      }
      case 'date': {
        const aDate = new Date(a.scraped_at || a.created_at).getTime();
        const bDate = new Date(b.scraped_at || b.created_at).getTime();
        comparison = aDate - bDate;
        break;
      }
    }

    return sortOrder === 'asc' ? comparison : -comparison;
  });

  return sorted;
};