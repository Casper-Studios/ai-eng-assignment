import { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Dashboard } from './pages/Dashboard';
import { RecipeDetail } from './pages/RecipeDetail';
import { ErrorBoundary } from './components/ErrorBoundary';
import type { EnhancedRecipe } from './types/recipe.types';

function App() {
  const [selectedRecipe, setSelectedRecipe] = useState<EnhancedRecipe | null>(null);

  const handleRecipeSelect = (recipe: EnhancedRecipe) => {
    setSelectedRecipe(recipe);
  };

  const handleBackToDashboard = () => {
    setSelectedRecipe(null);
  };

  return (
    <ErrorBoundary>
      <div className="App">
        <Router>
          <Routes>
            <Route
              path="/"
              element={
                selectedRecipe ? (
                  <RecipeDetail
                    recipe={selectedRecipe}
                    onBack={handleBackToDashboard}
                  />
                ) : (
                  <Dashboard onRecipeSelect={handleRecipeSelect} />
                )
              }
            />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Router>
      </div>
    </ErrorBoundary>
  );
}

export default App;
