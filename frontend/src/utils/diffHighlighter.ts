import type { ModificationType } from '../types/recipe.types';

export interface DiffSegment {
  type: ModificationType | 'unchanged';
  text: string;
  originalIndex?: number;
  modifiedIndex?: number;
}

export interface IngredientDiff {
  original: string;
  modified: string;
  segments: DiffSegment[];
}

/**
 * Simple text diff algorithm for highlighting changes
 */
export const calculateTextDiff = (original: string, modified: string): DiffSegment[] => {
  const segments: DiffSegment[] = [];

  if (original === modified) {
    return [{ type: 'unchanged', text: original }];
  }

  // Simple word-based diff
  const originalWords = original.split(/(\s+)/);
  const modifiedWords = modified.split(/(\s+)/);

  const originalSet = new Set(originalWords);
  const modifiedSet = new Set(modifiedWords);

  // Find common words
  const commonWords = new Set([...originalWords].filter(word => modifiedSet.has(word)));

  // Process original words
  originalWords.forEach(word => {
    if (commonWords.has(word)) {
      segments.push({ type: 'unchanged', text: word });
    } else {
      segments.push({ type: 'removal', text: word });
    }
  });

  // Process added words
  modifiedWords.forEach(word => {
    if (!originalSet.has(word) && !commonWords.has(word)) {
      segments.push({ type: 'addition', text: word });
    }
  });

  return segments;
};

/**
 * Compares two ingredient lists and highlights differences
 */
export const compareIngredientLists = (
  originalIngredients: string[],
  modifiedIngredients: string[]
): IngredientDiff[] => {
  const diffs: IngredientDiff[] = [];
  const maxLength = Math.max(originalIngredients.length, modifiedIngredients.length);

  for (let i = 0; i < maxLength; i++) {
    const original = originalIngredients[i] || '';
    const modified = modifiedIngredients[i] || '';

    if (original && !modified) {
      // Ingredient was removed
      diffs.push({
        original,
        modified: '',
        segments: [{ type: 'removal', text: original }]
      });
    } else if (!original && modified) {
      // Ingredient was added
      diffs.push({
        original: '',
        modified,
        segments: [{ type: 'addition', text: modified }]
      });
    } else if (original && modified) {
      // Ingredient might be modified
      const segments = calculateTextDiff(original, modified);
      diffs.push({
        original,
        modified,
        segments
      });
    }
  }

  return diffs;
};

/**
 * Compares two instruction lists and highlights differences
 */
export const compareInstructionLists = (
  originalInstructions: string[],
  modifiedInstructions: string[]
): IngredientDiff[] => {
  const diffs: IngredientDiff[] = [];
  const maxLength = Math.max(originalInstructions.length, modifiedInstructions.length);

  for (let i = 0; i < maxLength; i++) {
    const original = originalInstructions[i] || '';
    const modified = modifiedInstructions[i] || '';

    if (original && !modified) {
      // Instruction was removed
      diffs.push({
        original,
        modified: '',
        segments: [{ type: 'removal', text: original }]
      });
    } else if (!original && modified) {
      // Instruction was added
      diffs.push({
        original: '',
        modified,
        segments: [{ type: 'addition', text: modified }]
      });
    } else if (original && modified) {
      // Instruction might be modified
      const segments = calculateTextDiff(original, modified);
      diffs.push({
        original,
        modified,
        segments
      });
    }
  }

  return diffs;
};

/**
 * Analyzes quantity changes in ingredients
 */
export const analyzeQuantityChanges = (original: string, modified: string): {
  hasQuantityChange: boolean;
  originalQuantity?: string;
  modifiedQuantity?: string;
  percentageChange?: number;
} => {
  // Simple regex to extract quantities (numbers followed by units)
  const quantityRegex = /(\d+(?:\.\d+)?)\s*(?:cups?|tbsp|tsp|oz|lbs?|grams?|ml|liters?)?/gi;

  const originalMatches = original.match(quantityRegex);
  const modifiedMatches = modified.match(quantityRegex);

  if (!originalMatches || !modifiedMatches) {
    return { hasQuantityChange: false };
  }

  const originalQty = parseFloat(originalMatches[0]);
  const modifiedQty = parseFloat(modifiedMatches[0]);

  if (isNaN(originalQty) || isNaN(modifiedQty)) {
    return { hasQuantityChange: false };
  }

  const percentageChange = ((modifiedQty - originalQty) / originalQty) * 100;

  return {
    hasQuantityChange: Math.abs(percentageChange) > 1, // 1% threshold
    originalQuantity: originalMatches[0],
    modifiedQuantity: modifiedMatches[0],
    percentageChange
  };
};

/**
 * Extracts modification keywords from review text
 */
export const extractModificationKeywords = (reviewText: string): string[] => {
  const keywords: string[] = [];
  const text = reviewText.toLowerCase();

  const modificationPatterns = [
    { pattern: /added?\s+([^,.]+)/g, type: 'addition' },
    { pattern: /used?\s+([^,.]+)\s+instead/g, type: 'substitution' },
    { pattern: /omitted?\s+([^,.]+)/g, type: 'removal' },
    { pattern: /doubled?\s+([^,.]+)/g, type: 'quantity' },
    { pattern: /halved?\s+([^,.]+)/g, type: 'quantity' },
    { pattern: /increased?\s+([^,.]+)/g, type: 'quantity' },
    { pattern: /reduced?\s+([^,.]+)/g, type: 'quantity' },
    { pattern: /baked?\s+at\s+(\d+)/g, type: 'temperature' },
    { pattern: /baked?\s+for\s+(\d+)/g, type: 'timing' }
  ];

  modificationPatterns.forEach(({ pattern, type }) => {
    let match;
    while ((match = pattern.exec(text)) !== null) {
      keywords.push(`${type}: ${match[1].trim()}`);
    }
  });

  return keywords;
};

/**
 * Generates a summary of changes between recipes
 */
export const generateChangeSummary = (
  originalIngredients: string[],
  modifiedIngredients: string[],
  originalInstructions: string[],
  modifiedInstructions: string[]
): {
  ingredientsAdded: number;
  ingredientsRemoved: number;
  ingredientsModified: number;
  instructionsAdded: number;
  instructionsRemoved: number;
  instructionsModified: number;
} => {
  const ingredientDiffs = compareIngredientLists(originalIngredients, modifiedIngredients);
  const instructionDiffs = compareInstructionLists(originalInstructions, modifiedInstructions);

  const ingredientChanges = ingredientDiffs.reduce(
    (acc, diff) => {
      if (!diff.original && diff.modified) acc.added++;
      else if (diff.original && !diff.modified) acc.removed++;
      else if (diff.original !== diff.modified) acc.modified++;
      return acc;
    },
    { added: 0, removed: 0, modified: 0 }
  );

  const instructionChanges = instructionDiffs.reduce(
    (acc, diff) => {
      if (!diff.original && diff.modified) acc.added++;
      else if (diff.original && !diff.modified) acc.removed++;
      else if (diff.original !== diff.modified) acc.modified++;
      return acc;
    },
    { added: 0, removed: 0, modified: 0 }
  );

  return {
    ingredientsAdded: ingredientChanges.added,
    ingredientsRemoved: ingredientChanges.removed,
    ingredientsModified: ingredientChanges.modified,
    instructionsAdded: instructionChanges.added,
    instructionsRemoved: instructionChanges.removed,
    instructionsModified: instructionChanges.modified
  };
};