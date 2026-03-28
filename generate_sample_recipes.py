#!/usr/bin/env python3
"""
Generate 10 diverse sample recipes with multi-change reviews for testing.
"""

import json
import random
from pathlib import Path
from datetime import datetime


def generate_recipe(recipe_id, title, ingredients, instructions, reviews_data):
    """Generate a complete recipe object."""
    return {
        "recipe_id": recipe_id,
        "title": title,
        "ingredients": ingredients,
        "instructions": instructions,
        "description": f"A delicious {title.lower()} recipe.",
        "servings": "4",
        "rating": {
            "value": round(random.uniform(4.0, 5.0), 1),
            "count": len(reviews_data)
        },
        "reviews": reviews_data
    }


def generate_review(text, rating, has_mod=True):
    """Generate a review object."""
    user_id = random.randint(1000, 9999)
    return {
        "text": text,
        "rating": rating,
        "username": f"user_{user_id}",
        "has_modification": has_mod
    }


# Recipe 1: Thai Green Curry
recipe_1 = generate_recipe(
    "10001",
    "Thai Green Curry",
    [
        "1 can (13.5 oz) coconut milk",
        "2 tbsp green curry paste",
        "1 lb chicken breast, sliced",
        "1 cup bamboo shoots",
        "1 cup Thai basil leaves",
        "2 tbsp fish sauce",
        "1 tbsp palm sugar",
        "2 kaffir lime leaves",
    ],
    [
        "Heat coconut milk in a wok over medium heat.",
        "Add curry paste and stir until fragrant.",
        "Add chicken and cook until no longer pink.",
        "Add bamboo shoots, fish sauce, and sugar.",
        "Simmer for 10 minutes.",
        "Add Thai basil and lime leaves before serving."
    ],
    [
        generate_review("I used light coconut milk instead of regular. Added a dash of lime juice at the end. Also threw in some snap peas for crunch. Turned out amazing!", 5),
        generate_review("Doubled the curry paste for extra heat. Will use more bamboo shoots next time. Used brown sugar instead of palm sugar.", 4),
        generate_review("Great recipe! I added a pinch of red pepper flakes and drizzled with sesame oil before serving.", 5),
        generate_review("Perfect as is. The whole family loved it.", 5),
    ]
)

# Recipe 2: Mediterranean Quinoa Salad
recipe_2 = generate_recipe(
    "10002",
    "Mediterranean Quinoa Salad",
    [
        "2 cups quinoa",
        "1 cucumber, diced",
        "1 cup cherry tomatoes, halved",
        "1/2 cup kalamata olives",
        "1/2 cup feta cheese, crumbled",
        "1/4 cup red onion, minced",
        "3 tbsp olive oil",
        "2 tbsp lemon juice",
        "Fresh parsley and mint",
    ],
    [
        "Cook quinoa according to package directions and let cool.",
        "Combine all vegetables in a large bowl.",
        "Add cooled quinoa to vegetables.",
        "Whisk together olive oil and lemon juice.",
        "Toss salad with dressing.",
        "Top with feta and fresh herbs."
    ],
    [
        generate_review("Used tri-color quinoa for visual appeal. Added a splash of balsamic vinegar. Also topped with toasted pine nuts. Wonderful!", 5),
        generate_review("Substituted goat cheese for feta. Used red wine vinegar instead of lemon. Added diced bell peppers too.", 4),
        generate_review("I drizzled with extra virgin olive oil and sprinkled with za'atar spice blend at the end.", 5),
        generate_review("Made this for a potluck and everyone asked for the recipe!", 5),
    ]
)

# Recipe 3: Classic Beef Stew
recipe_3 = generate_recipe(
    "10003",
    "Classic Beef Stew",
    [
        "2 lbs beef chuck, cubed",
        "4 cups beef broth",
        "1 cup red wine",
        "4 potatoes, cubed",
        "3 carrots, sliced",
        "2 onions, chopped",
        "2 tbsp tomato paste",
        "2 bay leaves",
        "Fresh thyme and rosemary",
    ],
    [
        "Brown beef in a large Dutch oven.",
        "Add onions and cook until soft.",
        "Stir in tomato paste and cook 1 minute.",
        "Add wine and scrape up browned bits.",
        "Add broth, potatoes, carrots, and herbs.",
        "Simmer covered for 2 hours until meat is tender."
    ],
    [
        generate_review("I added a splash of Worcestershire sauce and a dash of paprika. Also threw in some celery. Next time will use more broth for thinner consistency.", 5),
        generate_review("Used Guinness instead of red wine. Added parsnips along with potatoes. Sprinkled with fresh parsley before serving.", 5),
        generate_review("Perfect comfort food! I added a pinch of garlic powder and used vegetable broth instead.", 4),
        generate_review("Made this in the slow cooker - turned out great!", 5),
    ]
)

# Recipe 4: Chocolate Lava Cake
recipe_4 = generate_recipe(
    "10004",
    "Chocolate Lava Cake",
    [
        "4 oz dark chocolate",
        "1/2 cup butter",
        "1 cup powdered sugar",
        "2 eggs",
        "2 egg yolks",
        "6 tbsp flour",
        "Butter and cocoa for ramekins",
    ],
    [
        "Preheat oven to 425°F.",
        "Melt chocolate and butter together.",
        "Stir in powdered sugar.",
        "Whisk in eggs and yolks.",
        "Fold in flour.",
        "Pour into greased ramekins.",
        "Bake 12-14 minutes until edges are firm.",
        "Invert onto plates and serve immediately."
    ],
    [
        generate_review("Added a splash of vanilla extract and a pinch of sea salt. Drizzled with caramel sauce at the end. Absolute perfection!", 5),
        generate_review("Used milk chocolate instead of dark for kids. Sprinkled with powdered sugar before serving. Will add raspberries next time.", 4),
        generate_review("I topped with whipped cream and a dash of cinnamon. Also added a teaspoon of espresso powder to the batter.", 5),
        generate_review("Followed exactly and they were delicious!", 5),
    ]
)

# Recipe 5: Korean BBQ Tacos
recipe_5 = generate_recipe(
    "10005",
    "Korean BBQ Tacos",
    [
        "1 lb beef short ribs",
        "1/4 cup soy sauce",
        "2 tbsp sesame oil",
        "2 tbsp brown sugar",
        "4 cloves garlic, minced",
        "1 tsp ginger, grated",
        "8 small corn tortillas",
        "1 cup kimchi",
        "Sesame seeds and green onions",
    ],
    [
        "Mix soy sauce, sesame oil, sugar, garlic, and ginger.",
        "Marinate beef for 2 hours.",
        "Grill beef over high heat, 3-4 minutes per side.",
        "Slice beef thinly against the grain.",
        "Warm tortillas on the grill.",
        "Assemble tacos with beef, kimchi, and toppings."
    ],
    [
        generate_review("I added a squeeze of lime juice and a dash of gochujang sauce. Also topped with fresh cilantro. Amazing flavor fusion!", 5),
        generate_review("Used pork instead of beef. Added sliced radishes and a pinch of cayenne pepper. Drizzled with sriracha mayo.", 4),
        generate_review("Perfect! I added a splash of rice vinegar and sprinkled with toasted sesame seeds.", 5),
        generate_review("Best tacos ever! The whole family loved them.", 5),
    ]
)

# Recipe 6: Vegan Buddha Bowl
recipe_6 = generate_recipe(
    "10006",
    "Vegan Buddha Bowl",
    [
        "1 cup quinoa",
        "1 block firm tofu, cubed",
        "2 cups mixed greens",
        "1 avocado, sliced",
        "1 cup cherry tomatoes",
        "1 cup shredded carrots",
        "1/4 cup tahini",
        "2 tbsp lemon juice",
        "Sesame seeds",
    ],
    [
        "Cook quinoa and let cool.",
        "Bake tofu at 400°F for 25 minutes until crispy.",
        "Arrange greens, vegetables, and avocado in bowls.",
        "Top with quinoa and tofu.",
        "Whisk tahini with lemon juice and water.",
        "Drizzle with tahini dressing.",
        "Sprinkle with sesame seeds."
    ],
    [
        generate_review("I added roasted sweet potato and a dash of smoked paprika. Also sprinkled with hemp seeds. Drizzled with tamari at the end.", 5),
        generate_review("Used chickpeas instead of tofu. Added sliced cucumber and a pinch of garlic powder. Will use more tahini next time.", 4),
        generate_review("Perfect! I topped with crushed peanuts and a splash of rice vinegar.", 5),
        generate_review("Great meal prep recipe!", 5),
    ]
)

# Recipe 7: French Onion Soup
recipe_7 = generate_recipe(
    "10007",
    "French Onion Soup",
    [
        "6 large onions, thinly sliced",
        "4 tbsp butter",
        "1 tsp sugar",
        "6 cups beef broth",
        "1/2 cup dry white wine",
        "1 tsp thyme",
        "1 bay leaf",
        "8 slices French bread",
        "2 cups Gruyère cheese, grated",
    ],
    [
        "Caramelize onions in butter over low heat, 30 minutes.",
        "Stir in sugar and cook 5 more minutes.",
        "Add wine and simmer 2 minutes.",
        "Add broth, thyme, and bay leaf.",
        "Simmer 30 minutes.",
        "Toast bread under broiler.",
        "Ladle soup into bowls, top with bread and cheese.",
        "Broil until cheese is melted and bubbly."
    ],
    [
        generate_review("I used a splash of sherry instead of wine. Added a pinch of nutmeg and a dash of Worcestershire sauce. Also added a sprinkle of Parmesan before broiling.", 5),
        generate_review("Used vegetable broth for a vegetarian version. Added a sprig of fresh thyme and a pinch of garlic powder. Will use more onions next time.", 4),
        generate_review("Perfect! I drizzled with a little olive oil and added a dash of black pepper.", 5),
        generate_review("Classic recipe, always turns out great!", 5),
    ]
)

# Recipe 8: Spicy Shrimp Tacos
recipe_8 = generate_recipe(
    "10008",
    "Spicy Shrimp Tacos",
    [
        "1 lb large shrimp, peeled",
        "2 tbsp olive oil",
        "2 tsp cumin",
        "1 tsp chili powder",
        "1/2 tsp cayenne pepper",
        "8 corn tortillas",
        "1 cup cabbage slaw",
        "1/2 cup sour cream",
        "Fresh cilantro",
        "Lime wedges",
    ],
    [
        "Mix spices with olive oil.",
        "Toss shrimp with spice mixture.",
        "Cook shrimp in a hot skillet, 2-3 minutes per side.",
        "Warm tortillas on the grill.",
        "Make slaw with cabbage and sour cream.",
        "Assemble tacos with shrimp and slaw.",
        "Top with cilantro and serve with lime."
    ],
    [
        generate_review("I added a squeeze of fresh lime juice and a dash of hot sauce. Also topped with pickled red onions. Sprinkled with cotija cheese at the end.", 5),
        generate_review("Used Greek yogurt instead of sour cream. Added sliced avocado and a pinch of smoked paprika. Will use more shrimp next time.", 4),
        generate_review("Perfect! I added a splash of tequila to the shrimp and sprinkled with fresh chopped cilantro.", 5),
        generate_review("Best shrimp tacos I've ever made!", 5),
    ]
)

# Recipe 9: Mushroom Risotto
recipe_9 = generate_recipe(
    "10009",
    "Mushroom Risotto",
    [
        "1.5 lbs mixed mushrooms",
        "2 cups Arborio rice",
        "6 cups chicken broth",
        "1 cup dry white wine",
        "1 shallot, minced",
        "3 cloves garlic, minced",
        "1/2 cup Parmesan cheese",
        "3 tbsp butter",
        "Fresh thyme",
    ],
    [
        "Sauté mushrooms until browned, set aside.",
        "Cook shallot and garlic in butter.",
        "Add rice and toast 2 minutes.",
        "Add wine and stir until absorbed.",
        "Add broth one ladle at a time, stirring constantly.",
        "Cook 18-20 minutes until rice is creamy.",
        "Fold in mushrooms, Parmesan, and butter.",
        "Top with fresh thyme."
    ],
    [
        generate_review("I used dried porcini mushrooms soaked in broth. Added a splash of truffle oil at the end. Also sprinkled with fresh parsley. Next time will use more wine.", 5),
        generate_review("Used vegetable broth for a lighter version. Added a pinch of nutmeg and a dash of white pepper. Topped with toasted pine nuts.", 4),
        generate_review("Perfect! I added a squeeze of lemon juice and a pinch of garlic powder.", 5),
        generate_review("Restaurant quality at home!", 5),
    ]
)

# Recipe 10: Berry Smoothie Bowl
recipe_10 = generate_recipe(
    "10010",
    "Berry Smoothie Bowl",
    [
        "2 cups frozen mixed berries",
        "1 frozen banana",
        "1/2 cup Greek yogurt",
        "1/2 cup almond milk",
        "2 tbsp honey",
        "Granola",
        "Fresh berries",
        "Chia seeds",
        "Coconut flakes",
    ],
    [
        "Blend frozen berries, banana, yogurt, milk, and honey.",
        "Pour into a bowl.",
        "Top with granola, fresh berries, chia seeds, and coconut.",
        "Serve immediately."
    ],
    [
        generate_review("I added a scoop of protein powder and a dash of cinnamon. Also topped with sliced almonds and a drizzle of almond butter. Sprinkled with bee pollen at the end.", 5),
        generate_review("Used coconut milk instead of almond. Added fresh spinach and a pinch of ginger. Will use less honey next time.", 4),
        generate_review("Perfect! I added a splash of vanilla extract and sprinkled with hemp seeds.", 5),
        generate_review("My daily breakfast now!", 5),
    ]
)

# Create all recipes
recipes = [recipe_1, recipe_2, recipe_3, recipe_4, recipe_5,
           recipe_6, recipe_7, recipe_8, recipe_9, recipe_10]

# Save to data directory
output_dir = Path("data/sample_recipes")
output_dir.mkdir(exist_ok=True)

for recipe in recipes:
    filename = f"recipe_{recipe['recipe_id']}_{recipe['title'].lower().replace(' ', '-')[:30]}.json"
    output_path = output_dir / filename

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(recipe, f, indent=2, ensure_ascii=False)

    print(f"✓ Created: {filename}")

print(f"\n{'='*80}")
print(f"Successfully created {len(recipes)} sample recipes!")
print(f"{'='*80}")
print(f"\nLocation: {output_dir}")
print(f"\nRecipe Summary:")
for recipe in recipes:
    mods_count = len([r for r in recipe['reviews'] if r['has_modification']])
    print(f"  • {recipe['title']}: {mods_count} reviews with modifications")

print(f"\n{'='*80}")
print("Test Coverage:")
print(f"{'='*80}")
print("✓ Asian cuisine (Thai curry, Korean tacos)")
print("✓ Mediterranean cuisine (Quinoa salad, Risotto)")
print("✓ American cuisine (Beef stew, Chocolate cake)")
print("✓ Mexican cuisine (Shrimp tacos)")
print("✓ Vegan/Plant-based (Buddha bowl)")
print("✓ French cuisine (Onion soup)")
print("✓ Breakfast/Smoothies")
print("\nAll recipes include multi-change reviews with:")
print("  • Finishing touches (drizzled, sprinkled, topped)")
print("  • Spice additions (dash, pinch, splash)")
print("  • Substitutions (milk, cheese, oils)")
print("  • Liquid adjustments (more/less broth)")
