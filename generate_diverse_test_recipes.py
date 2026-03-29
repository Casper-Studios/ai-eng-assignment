#!/usr/bin/env python3
"""
Generate 20 diverse test recipes with realistic review distributions.

Includes:
- High-rated reviews with modifications (4-5 stars)
- Low-rated reviews without modifications (1-3 stars)
- Reviews with no modifications (all ratings)
- Edge cases and diverse modification patterns
"""

import json
import random
from pathlib import Path
from datetime import datetime


def generate_recipe(recipe_id, title, cuisine, ingredients, instructions, reviews):
    """Generate a recipe dictionary."""
    return {
        'recipe_id': recipe_id,
        'title': title,
        'cuisine': cuisine,
        'ingredients': ingredients,
        'instructions': instructions,
        'reviews': reviews
    }


def create_diverse_reviews(base_reviews):
    """Create diverse review set from base reviews."""
    all_reviews = []

    # Add base reviews with modifications (4-5 stars)
    for review in base_reviews:
        all_reviews.append(review)

    # Add reviews without modifications
    no_mod_reviews = [
        {
            "username": f"Foodie{random.randint(100, 999)}",
            "rating": 5,
            "text": "Perfect recipe! Followed it exactly and turned out great. Will make again.",
            "has_modification": False
        },
        {
            "username": f"HomeCook{random.randint(100, 999)}",
            "rating": 4,
            "text": "Really good recipe. My family loved it. Simple to follow.",
            "has_modification": False
        },
        {
            "username": f"Critic{random.randint(100, 999)}",
            "rating": 3,
            "text": "It was okay. Nothing special but edible. Might make again with changes.",
            "has_modification": False
        },
        {
            "username": f"Disappointed{random.randint(100, 999)}",
            "rating": 2,
            "text": "Didn't work for me. Flavor was off and texture was wrong.",
            "has_modification": False
        },
    ]

    # Add a mix of no-mod reviews
    all_reviews.extend(no_mod_reviews)

    return all_reviews


# 20 diverse recipes
RECIPES = [
    # 1. Italian Pasta - diverse review mix
    generate_recipe(
        "5001",
        "Classic Spaghetti Carbonara",
        "Italian",
        [
            "1 lb spaghetti",
            "6 oz pancetta or guanciale, diced",
            "4 large egg yolks",
            "1 cup Pecorino Romano cheese, grated",
            "1/2 cup Parmesan cheese, grated",
            "Freshly ground black pepper",
            "Salt"
        ],
        [
            "Bring a large pot of salted water to boil.",
            "Cook spaghetti until al dente.",
            "Fry pancetta until crisp.",
            "Whisk egg yolks with cheeses and pepper.",
            "Toss hot pasta with pancetta, remove from heat.",
            "Add egg mixture and toss quickly."
        ],
        create_diverse_reviews([
            {
                "username": "ChefMario",
                "rating": 5,
                "text": "Absolutely perfect! I used thick-cut bacon instead of pancetta and added a splash of pasta water at the end. The consistency was creamy and delicious.",
                "has_modification": True
            },
            {
                "username": "HomeCook123",
                "rating": 4,
                "text": "Good recipe but needed more salt. I added extra Pecorino and a pinch of red pepper flakes for some heat.",
                "has_modification": True
            }
        ])
    ),

    # 2. Thai Curry
    generate_recipe(
        "5002",
        "Thai Green Curry Chicken",
        "Thai",
        [
            "1 lb chicken breast, sliced",
            "2 tbsp green curry paste",
            "400ml coconut milk",
            "1 cup bamboo shoots",
            "1 cup Thai basil leaves",
            "2 tbsp fish sauce",
            "1 tbsp palm sugar",
            "2 kaffir lime leaves"
        ],
        [
            "Heat curry paste in a wok until fragrant.",
            "Add chicken and cook through.",
            "Pour in coconut milk and simmer.",
            "Add bamboo shoots and seasonings.",
            "Stir in Thai basil just before serving."
        ],
        create_diverse_reviews([
            {
                "username": "SpicyFoodie",
                "rating": 5,
                "text": "Amazing curry! I added a dash of fish sauce and squeeze of lime juice at the end for extra brightness. Also threw in some baby corn and bell peppers.",
                "has_modification": True
            },
            {
                "username": "CurryLover",
                "rating": 4,
                "text": "Used 2% milk instead of coconut milk for a lighter version. Added extra curry paste and topped with crushed peanuts.",
                "has_modification": True
            }
        ])
    ),

    # 3. Mexican Tacos
    generate_recipe(
        "5003",
        "Carne Asada Tacos",
        "Mexican",
        [
            "1.5 lb flank steak",
            "3 limes, juiced",
            "4 orange juice",
            "6 garlic cloves, minced",
            "1 tsp cumin",
            "1 tsp chili powder",
            "Corn tortillas",
            "Cilantro, onions, salsa for serving"
        ],
        [
            "Marinate steak in citrus mixture for 4 hours.",
            "Grill steak over high heat.",
            "Let rest, then slice against the grain.",
            "Warm tortillas.",
            "Assemble tacos with toppings."
        ],
        create_diverse_reviews([
            {
                "username": "TacoKing",
                "rating": 5,
                "text": "Best tacos ever! Marinated for 24 hours instead of 4. Added a dash of cumin and squeeze of lime right before serving.",
                "has_modification": True
            },
            {
                "username": "GrillMaster",
                "rating": 4,
                "text": "Great flavor! I topped with cotija cheese and a drizzle of sour cream. Next time will add more jalapenos.",
                "has_modification": True
            }
        ])
    ),

    # 4. Indian Butter Chicken
    generate_recipe(
        "5004",
        "Butter Chicken (Murgh Makhani)",
        "Indian",
        [
            "2 lb chicken thighs, cubed",
            "1 cup yogurt",
            "2 tbsp garam masala",
            "1 tbsp turmeric",
            "2 cups tomato puree",
            "1 cup heavy cream",
            "4 tbsp butter",
            "1 tbsp ginger-garlic paste"
        ],
        [
            "Marinate chicken in yogurt and spices.",
            "Grill or bake chicken pieces.",
            "Make sauce with butter, tomato, ginger-garlic.",
            "Add cream and simmer.",
            "Add chicken to sauce and serve."
        ],
        create_diverse_reviews([
            {
                "username": "DesiChef",
                "rating": 5,
                "text": "Restaurant quality! I used coconut milk instead of heavy cream for a lighter version. Added a pinch of kasuri methi (dried fenugreek) at the end.",
                "has_modification": True
            },
            {
                "username": "SpicyQueen",
                "rating": 4,
                "text": "Delicious! Added extra garam masala and a dash of cream at the end. Served over basmati rice with naan.",
                "has_modification": True
            }
        ])
    ),

    # 5. French Onion Soup
    generate_recipe(
        "5005",
        "Classic French Onion Soup",
        "French",
        [
            "6 large yellow onions, sliced",
            "4 tbsp butter",
            "1 tsp sugar",
            "6 cups beef broth",
            "1/2 cup white wine",
            "1 bay leaf",
            "1 thyme sprig",
            "French bread, Gruyere cheese"
        ],
        [
            "Caramelize onions slowly in butter.",
            "Add sugar and continue cooking.",
            "Deglaze with wine.",
            "Add broth and herbs, simmer.",
            "Toast bread with cheese.",
            "Serve soup topped with bread."
        ],
        create_diverse_reviews([
            {
                "username": "FrenchCook",
                "rating": 5,
                "text": "Perfect! I added a splash of sherry instead of white wine and a pinch of nutmeg to deepen the flavor. Also drizzled with balsamic before serving.",
                "has_modification": True
            },
            {
                "username": "SoupLover",
                "rating": 4,
                "text": "Great recipe! Used a combination of Swiss and Gruyere. Added a dash of Worcestershire sauce for umami.",
                "has_modification": True
            }
        ])
    ),

    # 6. Japanese Ramen
    generate_recipe(
        "5006",
        "Tonkotsu Ramen",
        "Japanese",
        [
            "3 lb pork bones",
            "1 lb pork belly",
            "4 packages ramen noodles",
            "6 soft-boiled eggs",
            "4 green onions, sliced",
            "2 cups nori sheets",
            "1 cup soy sauce",
            "1 tbsp mirin"
        ],
        [
            "Boil pork bones for 12 hours.",
            "Chashu: braise pork belly in soy sauce.",
            "Cook ramen noodles.",
            "Assemble bowls with broth, noodles, toppings.",
            "Add soft-boiled egg, nori, green onions."
        ],
        create_diverse_reviews([
            {
                "username": "RamenMaster",
                "rating": 5,
                "text": "Incredible! I added a splash of sesame oil at the end and topped with corn and butter. Also added a dash of chili oil for heat.",
                "has_modification": True
            },
            {
                "username": "NoodleFan",
                "rating": 4,
                "text": "Used chicken broth instead of pork for a lighter version. Added extra green onions and a squeeze of lime.",
                "has_modification": True
            }
        ])
    ),

    # 7. Greek Salad
    generate_recipe(
        "5007",
        "Greek Village Salad",
        "Greek",
        [
            "4 large tomatoes, chunked",
            "1 cucumber, sliced",
            "1 red onion, sliced",
            "1 cup Kalamata olives",
            "8 oz feta cheese, cubed",
            "1/4 cup olive oil",
            "2 tbsp red wine vinegar",
            "1 tsp dried oregano"
        ],
        [
            "Combine vegetables in a large bowl.",
            "Add olives and feta.",
            "Whisk oil and vinegar.",
            "Toss salad with dressing.",
            "Sprinkle with oregano."
        ],
        create_diverse_reviews([
            {
                "username": "GreekChef",
                "rating": 5,
                "text": "Perfect summer salad! Added a splash of red wine vinegar and a pinch of sea salt. Also added capers and fresh mint.",
                "has_modification": True
            },
            {
                "username": "MediterraneanFan",
                "rating": 4,
                "text": "Added bell peppers and a drizzle of balsamic glaze. Used sheep's milk feta for extra creaminess.",
                "has_modification": True
            }
        ])
    ),

    # 8. American BBQ Ribs
    generate_recipe(
        "5008",
        "BBQ Baby Back Ribs",
        "American",
        [
            "2 racks baby back ribs",
            "2 tbsp brown sugar",
            "1 tbsp paprika",
            "1 tbsp garlic powder",
            "1 tsp chili powder",
            "1 cup BBQ sauce",
            "1/4 cup apple cider vinegar"
        ],
        [
            "Remove membrane from ribs.",
            "Rub with spice mixture.",
            "Grill low and slow for 3 hours.",
            "Brush with BBQ sauce.",
            "Rest and serve."
        ],
        create_diverse_reviews([
            {
                "username": "Pitmaster",
                "rating": 5,
                "text": "Fall-off-the-bone tender! I added a splash of apple cider vinegar to the BBQ sauce and a dash of smoked paprika. Also drizzled with honey at the end.",
                "has_modification": True
            },
            {
                "username": "BBQLover",
                "rating": 4,
                "text": "Great ribs! Added extra brown sugar and a pinch of cayenne. Served with coleslaw and cornbread.",
                "has_modification": True
            }
        ])
    ),

    # 9. Vietnamese Pho
    generate_recipe(
        "5009",
        "Beef Pho",
        "Vietnamese",
        [
            "3 lb beef bones",
            "1 lb beef brisket",
            "1 star anise",
            "1 cinnamon stick",
            "4 cloves",
            "1 onion, charred",
            "1 lb rice noodles",
            "Bean sprouts, basil, lime for serving"
        ],
        [
            "Roast bones and onion.",
            "Simmer bones with spices for 6 hours.",
            "Slice brisket thin.",
            "Cook noodles.",
            "Assemble bowls with broth, noodles, meat.",
            "Serve with herbs and condiments."
        ],
        create_diverse_reviews([
            {
                "username": "PhoFanatic",
                "rating": 5,
                "text": "Authentic taste! Added a splash of fish sauce and a pinch of sugar. Added a dash of hoisin sauce and squeeze of lime before eating.",
                "has_modification": True
            },
            {
                "username": "SoupLover",
                "rating": 4,
                "text": "Used chicken broth instead of beef. Added extra cinnamon and a pinch of star anise. Topped with sliced jalapenos.",
                "has_modification": True
            }
        ])
    ),

    # 10. Spanish Paella
    generate_recipe(
        "5010",
        "Seafood Paella",
        "Spanish",
        [
            "2 cups bomba rice",
            "1 lb shrimp",
            "1 lb mussels",
            "1/2 lb chorizo",
            "4 cups fish stock",
            "1 tsp saffron",
            "1 onion, diced",
            "4 garlic cloves, minced",
            "1 cup frozen peas"
        ],
        [
            "Toast saffron in hot stock.",
            "Cook chorizo, onion, garlic.",
            "Add rice and toast.",
            "Add stock and simmer.",
            "Add seafood in last 10 minutes.",
            "Let rest before serving."
        ],
        create_diverse_reviews([
            {
                "username": "SpanishChef",
                "rating": 5,
                "text": "Perfect paella! Added a splash of white wine and a pinch of smoked paprika. Also added a dash of lemon juice before serving.",
                "has_modification": True
            },
            {
                "username": "SeafoodLover",
                "rating": 4,
                "text": "Added scallops and calamari. Used a pinch of saffron and a drizzle of olive oil at the end.",
                "has_modification": True
            }
        ])
    ),

    # 11-20. Add more recipes with same pattern...
    # (Continuing with remaining cuisines)
]

# Add remaining 10 recipes
remaining_recipes = [
    # Moroccan
    generate_recipe(
        "5011",
        "Chicken Tagine with Preserved Lemons",
        "Moroccan",
        ["2 lb chicken thighs", "2 preserved lemons", "1 cup green olives", "1 onion", "4 garlic cloves", "1 tsp cumin", "1 tsp coriander", "1 tsp turmeric", "1 cup chicken stock", "1/4 cup cilantro"],
        ["Brown chicken in tagine.", "Cook onion and spices.", "Add chicken back with stock.", "Simmer 45 minutes.", "Add lemons and olives.", "Garnish with cilantro."],
        create_diverse_reviews([
            {"username": "MoroccanCook", "rating": 5, "text": "Incredible flavors! Added a splash of chicken stock and a pinch of ras el hanout. Also added a dash of lemon juice and a sprinkle of fresh cilantro.", "has_modification": True},
            {"username": "TagineLover", "rating": 4, "text": "Used dried apricots instead of olives. Added extra cumin and a pinch of cinnamon. Served over couscous.", "has_modification": True}
        ])
    ),

    # Korean
    generate_recipe(
        "5012",
        "Bibimbap",
        "Korean",
        ["2 cups cooked rice", "1 lb beef bulgogi", "1 cup spinach", "1 cup bean sprouts", "1 carrot", "1 zucchini", "4 eggs", "Gochujang sauce", "Sesame oil"],
        ["Season and cook vegetables.", "Cook bulgogi.", "Fry eggs.", "Arrange rice in bowl.", "Top with vegetables, beef, egg.", "Serve with gochujang."],
        create_diverse_reviews([
            {"username": "KoreanChef", "rating": 5, "text": "Restaurant quality at home! Added a splash of sesame oil and a pinch of gochugaru. Also added a dash of soy sauce and topped with sesame seeds.", "has_modification": True},
            {"username": "BibimbapLover", "rating": 4, "text": "Used tofu instead of beef. Added extra vegetables and a drizzle of chili oil. Served with kimchi on the side.", "has_modification": True}
        ])
    ),

    # Brazilian
    generate_recipe(
        "5013",
        "Feijoada Completa",
        "Brazilian",
        ["2 lb black beans", "1 lb pork shoulder", "1/2 lb chorizo", "1/2 lb bacon", "2 bay leaves", "4 oranges", "White rice", "Collard greens"],
        ["Simmer beans with smoked meats.", "Cook until beans are tender.", "Season and finish.", "Serve over white rice.", "Garnish with orange slices.", "Serve with sauteed collard greens."],
        create_diverse_reviews([
            {"username": "BrazilianChef", "rating": 5, "text": "Authentic and delicious! Added a splash of lime juice and a pinch of sea salt. Also added a dash of hot sauce and topped with fresh cilantro.", "has_modification": True},
            {"username": "FeijoadaFan", "rating": 4, "text": "Used ham hocks instead of pork shoulder. Added extra bay leaves and a pinch of black pepper. Served with farofa.", "has_modification": True}
        ])
    ),

    # Lebanese
    generate_recipe(
        "5014",
        "Kibbeh",
        "Lebanese",
        ["2 lb bulgur wheat", "1 lb ground beef", "1 lb ground lamb", "2 onions", "1 tsp allspice", "1 tsp cinnamon", "1/2 cup pine nuts", "Vegetable oil"],
        ["Soak bulgur in water.", "Mix bulgur with meat and spices.", "Make filling with meat, onions, nuts.", "Form into football shapes.", "Fry until golden brown.", "Serve with yogurt sauce."],
        create_diverse_reviews([
            {"username": "LebaneseCook", "rating": 5, "text": "Perfect kibbeh! Added a splash of lemon juice and a pinch of sumac. Also added a dash of allspice and a sprinkle of fresh mint.", "has_modification": True},
            {"username": "MiddleEasternFan", "rating": 4, "text": "Baked instead of fried for a lighter version. Added extra pine nuts and a pinch of cumin. Served with tahini sauce.", "has_modification": True}
        ])
    ),

    # Ethiopian
    generate_recipe(
        "5015",
        "Doro Wat",
        "Ethiopian",
        ["1 whole chicken", "4 onions", "4 tbsp berbere spice", "4 tbsp niter kibbeh", "4 garlic cloves", "1 inch ginger", "4 hard-boiled eggs", "Injera flatbread"],
        ["Cook onions slowly until browned.", "Add berbere and niter kibbeh.", "Add chicken and cook.", "Add garlic and ginger.", "Simmer until chicken is done.", "Add eggs and serve with injera."],
        create_diverse_reviews([
            {"username": "EthiopianChef", "rating": 5, "text": "Incredible! Added a splash of lemon juice and a pinch of cardamom. Also added a dash of berbere and topped with fresh cilantro.", "has_modification": True},
            {"username": "SpicyFoodie", "rating": 4, "text": "Used extra berbere for more heat. Added a splash of water and a pinch of salt. Served with extra injera.", "has_modification": True}
        ])
    ),

    # Polish
    generate_recipe(
        "5016",
        "Pierogi Ruskie",
        "Polish",
        ["2 cups flour", "1 egg", "1/2 cup sour cream", "4 potatoes", "1 cup cheese", "1 onion", "Butter for serving", "Sour cream for serving"],
        ["Make dough with flour, egg, sour cream.", "Boil and mash potatoes.", "Mix with cheese and caramelized onion.", "Roll dough and fill.", "Boil pierogi.", "Serve with butter and sour cream."],
        create_diverse_reviews([
            {"username": "PolishChef", "rating": 5, "text": "Just like grandma's! Added a pinch of salt and a dash of pepper. Also added a splash of sour cream and topped with fried onions.", "has_modification": True},
            {"username": "DumplingLover", "rating": 4, "text": "Added bacon and cheddar cheese. Also added a pinch of garlic powder and a drizzle of melted butter.", "has_modification": True}
        ])
    ),

    # Peruvian
    generate_recipe(
        "5017",
        "Ceviche de Pescado",
        "Peruvian",
        ["1 lb white fish", "1 cup lime juice", "1 red onion", "1 jalapeno", "1 cilantro bunch", "1 tsp salt", "Corn and sweet potato"],
        ["Marinate fish in lime juice.", "Let cure for 20 minutes.", "Add onion, jalapeno, cilantro.", "Season with salt.", "Serve immediately.", "Accompany with corn and sweet potato."],
        create_diverse_reviews([
            {"username": "PeruvianChef", "rating": 5, "text": "Fresh and perfect! Added a splash of lime juice and a pinch of chili powder. Also added a dash of hot sauce and topped with extra cilantro.", "has_modification": True},
            {"username": "CevicheLover", "rating": 4, "text": "Added shrimp and scallops. Added extra jalapeno and a pinch of cumin. Served with plantain chips.", "has_modification": True}
        ])
    ),

    # Turkish
    generate_recipe(
        "5018",
        "Baklava",
        "Turkish",
        ["1 package phyllo dough", "2 cups pistachios", "1 cup sugar", "1 tsp cinnamon", "1 cup butter", "1 cup water", "1 cup sugar", "1 lemon juice"],
        ["Mix nuts with sugar and cinnamon.", "Layer phyllo with butter.", "Add nut mixture.", "Repeat layers.", "Cut before baking.", "Make syrup and pour hot over cold baklava."],
        create_diverse_reviews([
            {"username": "TurkishChef", "rating": 5, "text": "Perfect baklava! Added a splash of lemon juice and a pinch of cardamom to the syrup. Also added a dash of rose water and topped with extra pistachios.", "has_modification": True},
            {"username": "DessertLover", "rating": 4, "text": "Used walnuts instead of pistachios. Added extra cinnamon and a pinch of clove. Served with vanilla ice cream.", "has_modification": True}
        ])
    ),

    # Jamaican
    generate_recipe(
        "5019",
        "Jerk Chicken",
        "Jamaican",
        ["2 lb chicken thighs", "2 scotch bonnet peppers", "1 onion", "4 garlic cloves", "1 inch ginger", "2 tbsp allspice", "1 tbsp thyme", "1 cinnamon stick", "2 tbsp soy sauce", "2 tbsp brown sugar"],
        ["Blend peppers, onion, garlic, ginger.", "Add spices and marinade chicken.", "Let marinate 4 hours.", "Grill over charcoal.", "Baste with remaining marinade.", "Serve with rice and peas."],
        create_diverse_reviews([
            {"username": "JamaicanChef", "rating": 5, "text": "Authentic heat! Added a splash of soy sauce and a pinch of nutmeg. Also added a dash of lime juice and topped with green onions.", "has_modification": True},
            {"username": "SpicyFoodie", "rating": 4, "text": "Reduced scotch bonnet peppers for less heat. Added extra brown sugar and a pinch of paprika. Served with mango salsa.", "has_modification": True}
        ])
    ),

    # Australian
    generate_recipe(
        "5020",
        "Pavlova",
        "Australian",
        ["4 egg whites", "1 cup sugar", "1 tsp vinegar", "1 tsp cornstarch", "1 tsp vanilla", "1 cup heavy cream", "Fresh fruits"],
        ["Beat egg whites until soft peaks.", "Gradually add sugar.", "Fold in vinegar, cornstarch, vanilla.", "Bake at low heat for 1 hour.", "Cool in oven.", "Top with whipped cream and fruits."],
        create_diverse_reviews([
            {"username": "AustralianChef", "rating": 5, "text": "Perfect pavlova! Added a splash of vanilla and a pinch of salt. Also added a dash of lemon zest and topped with passion fruit.", "has_modification": True},
            {"username": "DessertLover", "rating": 4, "text": "Used berries and kiwi for topping. Added extra vanilla and a pinch of cream of tartar. Served with mango coulis.", "has_modification": True}
        ])
    ),
]

# Combine all recipes
ALL_RECIPES = RECIPES + remaining_recipes


def main():
    """Generate 20 diverse test recipes."""

    print("=" * 80)
    print("Generating 20 Diverse Test Recipes with Realistic Review Distributions")
    print("=" * 80)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    output_dir = Path("data")
    output_dir.mkdir(exist_ok=True)

    # Save all recipes
    for recipe in ALL_RECIPES:
        filename = f"recipe_{recipe['recipe_id']}_{recipe['title'].lower().replace(' ', '-')[:50]}.json"
        filepath = output_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(recipe, f, indent=2, ensure_ascii=False)

        print(f"✓ {filename}")
        print(f"  Cuisine: {recipe['cuisine']}")
        print(f"  Reviews: {len(recipe['reviews'])} ({sum(1 for r in recipe['reviews'] if r['has_modification'])} with modifications)")

        # Show rating distribution
        ratings = [r['rating'] for r in recipe['reviews']]
        print(f"  Ratings: {min(ratings)}-{max(ratings)}★")
        print()

    print("=" * 80)
    print(f"Generated {len(ALL_RECIPES)} recipes successfully!")
    print("=" * 80)
    print()

    # Statistics
    cuisines = {}
    for recipe in ALL_RECIPES:
        cuisine = recipe['cuisine']
        cuisines[cuisine] = cuisines.get(cuisine, 0) + 1

    print("Cuisine Distribution:")
    for cuisine, count in sorted(cuisines.items()):
        print(f"  • {cuisine}: {count}")

    print()
    total_reviews = sum(len(r['reviews']) for r in ALL_RECIPES)
    total_modifications = sum(sum(1 for r in recipe['reviews'] if r['has_modification']) for recipe in ALL_RECIPES)
    total_high_rated = sum(sum(1 for r in recipe['reviews'] if r['rating'] >= 4) for recipe in ALL_RECIPES)

    print(f"Total Reviews: {total_reviews}")
    print(f"Total with Modifications: {total_modifications}")
    print(f"Total High-Rated (≥4★): {total_high_rated}")
    print(f"Average per Recipe: {total_reviews/len(ALL_RECIPES):.1f} reviews")

    print()
    print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
