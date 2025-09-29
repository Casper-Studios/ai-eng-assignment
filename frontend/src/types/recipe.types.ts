export interface RecipeRating {
  value: string;
  count: string;
}

export interface RecipeNutrition {
  '@type': string;
  calories: string;
  carbohydrateContent: string;
  cholesterolContent: string;
  fiberContent: string;
  proteinContent: string;
  saturatedFatContent: string;
  sodiumContent: string;
  fatContent: string;
  unsaturatedFatContent: string;
}

export interface RecipeReview {
  text: string;
  rating: number;
  has_modification?: boolean;
  is_featured?: boolean;
}

export interface FeaturedTweak extends RecipeReview {
  is_featured: true;
  has_modification: true;
}

// Updated interface for the actual enhanced recipe structure from the pipeline
export interface EnhancedRecipe {
  recipe_id: string;
  original_recipe_id: string;
  title: string;
  description: string;
  ingredients: string[];
  instructions: string[];
  modifications_applied: ModificationApplied[];
  enhancement_summary: EnhancementSummary;
  servings: string;
  prep_time?: string | null;
  cook_time?: string | null;
  total_time?: string | null;
  created_at: string;
  pipeline_version: string;

  // Legacy properties for backward compatibility
  url?: string;
  scraped_at?: string;
  rating?: RecipeRating;
  preptime?: string;
  cooktime?: string;
  totaltime?: string;
  nutrition?: RecipeNutrition;
  author?: string;
  categories?: string[];
  featured_tweaks?: FeaturedTweak[];
  reviews?: RecipeReview[];
}

export interface ModificationApplied {
  source_review: {
    text: string;
    reviewer: string | null;
    rating: number;
  };
  modification_type: string;
  reasoning: string;
  changes_made: ModificationChange[];
}

export interface ModificationChange {
  type: string;
  from_text?: string;
  to_text?: string;
  operation: 'add' | 'replace' | 'remove';
}

export interface EnhancementSummary {
  total_changes: number;
  change_types: string[];
  expected_impact: string;
}

export interface OriginalRecipe {
  url: string;
  scraped_at: string;
  recipe_id: string;
  title: string;
  description: string;
  rating?: RecipeRating;
  preptime: string;
  cooktime: string;
  totaltime: string;
  servings: string;
  ingredients: string[];
  instructions: string[];
  nutrition: RecipeNutrition;
  author: string;
  categories: string[];
  featured_tweaks?: FeaturedTweak[];
  reviews: RecipeReview[];
}

export interface RecipeComparison {
  original: OriginalRecipe;
  enhanced: EnhancedRecipe;
  modifications: ModificationDetail[];
}

export interface ModificationDetail {
  type: 'addition' | 'modification' | 'removal';
  category: 'ingredient' | 'instruction' | 'technique' | 'timing' | 'quantity';
  originalText?: string;
  modifiedText?: string;
  reason: string;
  source: RecipeReview;
  impact: ModificationImpact;
}

export interface ModificationImpact {
  flavor: 'positive' | 'neutral' | 'negative';
  texture: 'positive' | 'neutral' | 'negative';
  difficulty: 'easier' | 'same' | 'harder';
  time: 'faster' | 'same' | 'longer';
}

export interface EnhancementReport {
  total_recipes: number;
  successfully_enhanced: number;
  failed_enhancements: number;
  synthetic_reviews_added: number;
  subtle_modifications_found: number;
  enhanced_files: Array<{
    original_file: string;
    enhanced_file: string;
    modification_reviews: number;
    synthetic_added: boolean;
  }>;
  enhancement_success_rate: number;
  meets_80_percent_target: boolean;
}

export interface ValidationMetrics {
  multi_modification_accuracy: number;
  recipe_coverage: number;
  accuracy_score: number;
  safety_score: number;
  overall_pass_rate: number;
}

// Utility types for UI components
export interface RecipeCardProps {
  recipe: EnhancedRecipe;
  showComparison?: boolean;
  onSelect?: (recipe: EnhancedRecipe) => void;
}

export interface FilterOptions {
  categories: string[];
  minRating: number;
  hasModifications: boolean;
  sortBy: 'title' | 'rating' | 'modifications' | 'date';
  sortOrder: 'asc' | 'desc';
}

export type ModificationType = 'addition' | 'modification' | 'removal';
export type ModificationCategory = 'ingredient' | 'instruction' | 'technique' | 'timing' | 'quantity';