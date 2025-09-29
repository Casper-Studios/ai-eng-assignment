# Recipe Enhancement Showcase - Frontend

A modern React web application showcasing the Recipe Enhancement Pipeline with interactive comparisons, community feedback, and validation metrics.

## 🚀 Features

### 📊 Dashboard & Metrics
- **Validation Dashboard**: Real-time pipeline performance metrics and PRD compliance
- **Recipe Gallery**: Interactive grid of all 6 enhanced recipes with filtering and search
- **Enhancement Metrics**: Success rates, accuracy scores, and quality assurance results

### 🔍 Recipe Comparison
- **Side-by-Side View**: Compare original vs enhanced recipes in real-time
- **Interactive Toggle**: Switch between comparison, enhanced-only, and original-only views
- **Visual Highlighting**: Color-coded ingredients and instructions showing additions, modifications, and removals

### ✨ Modification Analysis
- **Detailed Diff Viewer**: Line-by-line comparison with visual highlighting
- **Change Summary**: Comprehensive statistics on modifications made
- **Modification Badges**: Categorized tags for different types of changes

### 💬 Community Features
- **Featured Tweaks**: Community-verified recipe modifications with ratings
- **Review Analysis**: Extraction and display of modification keywords
- **Impact Assessment**: Visual representation of community feedback

### 🎨 User Experience
- **Responsive Design**: Optimized for desktop, tablet, and mobile devices
- **Smooth Animations**: Framer Motion powered transitions and interactions
- **Error Handling**: Comprehensive error boundaries and loading states
- **Accessibility**: WCAG-compliant design with proper ARIA labels

## 🛠️ Tech Stack

- **React 18** with TypeScript for type-safe development
- **Vite** for lightning-fast development and optimized builds
- **Tailwind CSS** for utility-first styling and responsive design
- **Framer Motion** for smooth animations and micro-interactions
- **React Router** for client-side navigation
- **Lucide React** for consistent iconography

## 🔧 Installation & Setup

### Prerequisites
- Node.js 18+ and npm
- Access to the enhanced recipe data (symlinked from parent directory)

### Development Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

The application will be available at `http://localhost:5173`

## 📊 Data Integration

The frontend seamlessly integrates with the Recipe Enhancement Pipeline data:

- **Enhanced Recipes**: Located at `/data/enhanced/` (6 total recipes)
- **Validation Results**: Real-time metrics from the validation framework
- **Enhancement Report**: Success rates and processing statistics

### Supported Recipe Data
- ✅ Best Chocolate Chip Cookies (4 modifications)
- ✅ Creamy Sweet Potato Soup (5 modifications)
- ✅ Spicy Apple Cake (2 modifications)
- ✅ Nikujaga Japanese Meat & Potatoes (1 modification)
- ✅ Spiced Purple Plum Jam (2 modifications)
- ✅ Mango Teriyaki Marinade (2 modifications)

## 🎯 Key Components

### RecipeCard
Interactive recipe cards displaying:
- Recipe metadata (title, rating, time, servings)
- Community enhancement stats
- Featured tweak previews
- Modification counts

### RecipeComparison
Side-by-side comparison featuring:
- Original vs enhanced recipe views
- Real-time highlighting of changes
- Enhancement summary statistics
- View mode toggles

### ModificationHighlighter
Visual diff system with:
- Color-coded change indicators
- Line-by-line modification tracking
- Change type categorization
- Interactive hover tooltips

### FeaturedTweaks
Community feedback showcase:
- Star ratings and reviews
- Modification keyword extraction
- Expandable detailed descriptions
- Community impact metrics

## 🎨 Design System

### Color Palette
- **Primary**: Blue/teal for enhanced content
- **Secondary**: Orange for original content
- **Success**: Green for additions and improvements
- **Warning**: Yellow for modifications
- **Danger**: Red for removals

## ⚡ Performance

- **Code Splitting**: Automatic route-based splitting
- **Tree Shaking**: Unused code elimination
- **Bundle Analysis**: Optimized dependency bundling

## 🔒 Error Handling

- **Error Boundaries**: Graceful error recovery
- **Loading States**: Skeleton screens and spinners
- **Retry Mechanisms**: User-friendly error recovery

## 📱 Responsive Design

- **Mobile First**: Optimized for mobile devices
- **Tablet Support**: Adapted layouts for tablets
- **Desktop Enhancement**: Rich desktop experience

## 🚀 Production Ready

The application is optimized for production with Vite's build system and modern React patterns.

---

**Built to showcase the power of AI-driven recipe enhancement and community collaboration.**
