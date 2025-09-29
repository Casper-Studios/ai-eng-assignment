import { useState, useEffect } from 'react';
import type {
  RecipeComparison,
  OriginalRecipe,
  EnhancedRecipe
} from '../types/recipe.types';
import { createRecipeComparison, loadOriginalRecipe } from '../utils/recipeParser';
import {
  compareIngredientLists,
  compareInstructionLists,
  generateChangeSummary
} from '../utils/diffHighlighter';
import type { IngredientDiff } from '../utils/diffHighlighter';

export const useComparison = (enhancedRecipe: EnhancedRecipe | null) => {
  const [originalRecipe, setOriginalRecipe] = useState<OriginalRecipe | null>(null);
  const [comparison, setComparison] = useState<RecipeComparison | null>(null);
  const [ingredientDiffs, setIngredientDiffs] = useState<IngredientDiff[]>([]);
  const [instructionDiffs, setInstructionDiffs] = useState<IngredientDiff[]>([]);
  const [changeSummary, setChangeSummary] = useState({
    ingredientsAdded: 0,
    ingredientsRemoved: 0,
    ingredientsModified: 0,
    instructionsAdded: 0,
    instructionsRemoved: 0,
    instructionsModified: 0
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!enhancedRecipe) {
      setOriginalRecipe(null);
      setComparison(null);
      setIngredientDiffs([]);
      setInstructionDiffs([]);
      return;
    }

    const loadComparison = async () => {
      try {
        setLoading(true);
        setError(null);

        // Load original recipe - use original_recipe_id if available, fallback to recipe_id
        const originalId = enhancedRecipe.original_recipe_id || enhancedRecipe.recipe_id.replace('_enhanced', '');

        // Create a mapping of known original recipe filenames
        const originalFilenameMap: Record<string, string> = {
          '10813': 'recipe_10813_best-chocolate-chip-cookies.json',
          '77935': 'recipe_77935_creamy-sweet-potato-with-ginger-soup.json',
          '144299': 'recipe_144299_nikujaga-japanese-style-meat-and-potatoes-.json',
          '19117': 'recipe_19117_spicy-apple-cake.json',
          '284494': 'recipe_284494_spiced-purple-plum-jam.json',
          '45613': 'recipe_45613_mango-teriyaki-marinade.json'
        };

        const originalFilename = originalFilenameMap[originalId] || `recipe_${originalId}.json`;

        const original = await loadOriginalRecipe(originalFilename);
        setOriginalRecipe(original);

        // Create a mapping of enhanced recipe filenames
        const enhancedFilenameMap: Record<string, string> = {
          '10813_enhanced': 'enhanced_10813_best-chocolate-chip-cookies.json',
          '77935_enhanced': 'enhanced_77935_creamy-sweet-potato-with-ginge.json',
          '144299_enhanced': 'enhanced_144299_nikujaga-(japanese-style-meat-.json',
          '19117_enhanced': 'enhanced_19117_spicy-apple-cake.json'
        };

        const enhancedFilename = enhancedFilenameMap[enhancedRecipe.recipe_id] ||
          `enhanced_${originalId}_${enhancedRecipe.title
            .toLowerCase()
            .replace(/[^a-z0-9]+/g, '-')
            .replace(/^-|-$/g, '')}.json`;

        // Create comparison
        const comparisonData = await createRecipeComparison(
          enhancedFilename,
          originalFilename
        );
        setComparison(comparisonData);

        // Calculate diffs
        const ingredientDiffsData = compareIngredientLists(
          original.ingredients,
          enhancedRecipe.ingredients
        );
        setIngredientDiffs(ingredientDiffsData);

        const instructionDiffsData = compareInstructionLists(
          original.instructions,
          enhancedRecipe.instructions
        );
        setInstructionDiffs(instructionDiffsData);

        // Generate change summary
        const summary = generateChangeSummary(
          original.ingredients,
          enhancedRecipe.ingredients,
          original.instructions,
          enhancedRecipe.instructions
        );
        setChangeSummary(summary);

      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load comparison data');
        console.error('Error loading comparison:', err);
      } finally {
        setLoading(false);
      }
    };

    loadComparison();
  }, [enhancedRecipe]);

  // Helper functions
  const getTotalChanges = () => {
    return (
      changeSummary.ingredientsAdded +
      changeSummary.ingredientsRemoved +
      changeSummary.ingredientsModified +
      changeSummary.instructionsAdded +
      changeSummary.instructionsRemoved +
      changeSummary.instructionsModified
    );
  };

  const getChangeDescription = () => {
    const totalChanges = getTotalChanges();
    if (totalChanges === 0) return 'No changes detected';

    const parts: string[] = [];

    if (changeSummary.ingredientsAdded > 0) {
      parts.push(`${changeSummary.ingredientsAdded} ingredient${changeSummary.ingredientsAdded > 1 ? 's' : ''} added`);
    }
    if (changeSummary.ingredientsRemoved > 0) {
      parts.push(`${changeSummary.ingredientsRemoved} ingredient${changeSummary.ingredientsRemoved > 1 ? 's' : ''} removed`);
    }
    if (changeSummary.ingredientsModified > 0) {
      parts.push(`${changeSummary.ingredientsModified} ingredient${changeSummary.ingredientsModified > 1 ? 's' : ''} modified`);
    }
    if (changeSummary.instructionsAdded > 0) {
      parts.push(`${changeSummary.instructionsAdded} instruction${changeSummary.instructionsAdded > 1 ? 's' : ''} added`);
    }
    if (changeSummary.instructionsRemoved > 0) {
      parts.push(`${changeSummary.instructionsRemoved} instruction${changeSummary.instructionsRemoved > 1 ? 's' : ''} removed`);
    }
    if (changeSummary.instructionsModified > 0) {
      parts.push(`${changeSummary.instructionsModified} instruction${changeSummary.instructionsModified > 1 ? 's' : ''} modified`);
    }

    return parts.join(', ');
  };

  return {
    // Data
    originalRecipe,
    enhancedRecipe,
    comparison,
    ingredientDiffs,
    instructionDiffs,
    changeSummary,

    // State
    loading,
    error,

    // Helper functions
    getTotalChanges,
    getChangeDescription,

    // Stats
    hasChanges: getTotalChanges() > 0
  };
};