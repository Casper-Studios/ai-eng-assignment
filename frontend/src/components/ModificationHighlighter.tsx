import React from 'react';
import { Plus, Minus, Edit } from 'lucide-react';
import type { DiffSegment, IngredientDiff } from '../utils/diffHighlighter';

interface ModificationHighlighterProps {
  diffs: IngredientDiff[];
  title: string;
  type: 'ingredients' | 'instructions';
}

export const ModificationHighlighter: React.FC<ModificationHighlighterProps> = ({
  diffs,
  title,
  type
}) => {
  const renderDiffSegment = (segment: DiffSegment, index: number) => {
    const baseClasses = "modification-highlight inline";

    switch (segment.type) {
      case 'addition':
        return (
          <span key={index} className={`${baseClasses} modification-added`}>
            {segment.text}
          </span>
        );
      case 'removal':
        return (
          <span key={index} className={`${baseClasses} modification-removed line-through`}>
            {segment.text}
          </span>
        );
      case 'modification':
        return (
          <span key={index} className={`${baseClasses} modification-modified`}>
            {segment.text}
          </span>
        );
      default:
        return (
          <span key={index} className="inline">
            {segment.text}
          </span>
        );
    }
  };

  const getChangeIcon = (diff: IngredientDiff) => {
    if (!diff.original && diff.modified) {
      return <Plus className="w-4 h-4 text-green-600" />;
    }
    if (diff.original && !diff.modified) {
      return <Minus className="w-4 h-4 text-red-600" />;
    }
    if (diff.original !== diff.modified) {
      return <Edit className="w-4 h-4 text-yellow-600" />;
    }
    return null;
  };

  const getChangeDescription = (diff: IngredientDiff) => {
    if (!diff.original && diff.modified) {
      return 'Added';
    }
    if (diff.original && !diff.modified) {
      return 'Removed';
    }
    if (diff.original !== diff.modified) {
      return 'Modified';
    }
    return 'Unchanged';
  };

  const changesCount = diffs.filter(diff =>
    diff.original !== diff.modified || !diff.original || !diff.modified
  ).length;

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
        <div className="flex items-center space-x-2">
          <span className="text-sm text-gray-500">{changesCount} changes</span>
          <div className="flex items-center space-x-1">
            <div className="w-3 h-3 bg-green-100 border border-green-200 rounded"></div>
            <span className="text-xs text-gray-500">Added</span>
            <div className="w-3 h-3 bg-yellow-100 border border-yellow-200 rounded ml-2"></div>
            <span className="text-xs text-gray-500">Modified</span>
            <div className="w-3 h-3 bg-red-100 border border-red-200 rounded ml-2"></div>
            <span className="text-xs text-gray-500">Removed</span>
          </div>
        </div>
      </div>

      <div className="space-y-3">
        {diffs.map((diff, index) => {
          const hasChanges = diff.original !== diff.modified || !diff.original || !diff.modified;
          const changeIcon = getChangeIcon(diff);
          const changeDescription = getChangeDescription(diff);

          return (
            <div
              key={index}
              className={`p-3 rounded-lg border transition-all ${
                hasChanges
                  ? 'border-gray-300 bg-gray-50 hover:shadow-sm'
                  : 'border-gray-200 bg-white'
              }`}
            >
              {/* Change indicator */}
              {hasChanges && (
                <div className="flex items-center space-x-2 mb-2">
                  {changeIcon}
                  <span className="text-sm font-medium text-gray-700">
                    {changeDescription}
                  </span>
                </div>
              )}

              {/* Original text (if exists and different) */}
              {diff.original && hasChanges && (
                <div className="mb-2">
                  <div className="text-xs text-gray-500 mb-1">Original:</div>
                  <div className="p-2 bg-red-50 border border-red-200 rounded text-sm">
                    <span className="line-through text-red-700">{diff.original}</span>
                  </div>
                </div>
              )}

              {/* Modified text or segments */}
              {diff.modified && (
                <div>
                  {hasChanges && <div className="text-xs text-gray-500 mb-1">Enhanced:</div>}
                  <div className={`p-2 rounded text-sm ${
                    hasChanges ? 'bg-green-50 border border-green-200' : 'bg-gray-50 border border-gray-200'
                  }`}>
                    {diff.segments.length > 1 ? (
                      <span>
                        {diff.segments.map((segment, segIndex) =>
                          renderDiffSegment(segment, segIndex)
                        )}
                      </span>
                    ) : (
                      <span className={hasChanges ? 'text-green-700' : 'text-gray-700'}>
                        {diff.modified}
                      </span>
                    )}
                  </div>
                </div>
              )}

              {/* Removed item */}
              {!diff.modified && diff.original && (
                <div className="p-2 bg-red-50 border border-red-200 rounded text-sm">
                  <span className="line-through text-red-700">{diff.original}</span>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Summary */}
      {changesCount > 0 && (
        <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
          <div className="text-sm text-blue-800 font-medium">
            📊 Summary: {changesCount} {type} {changesCount === 1 ? 'was' : 'were'} modified in this enhanced recipe
          </div>
        </div>
      )}
    </div>
  );
};