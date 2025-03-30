# workouts/constants.py
TRUSTED_TRAINERS = [
    "Chloe Ting", "Pamela Reif", "Heather Robertson",
    "Yoga With Adriene", "Fitness Blender", "Blogilates",
    "MadFit", "POPSUGAR Fitness", "The Body Coach TV",
    "Emi Wong", "MrandMrsMuscle", "GrowingAnnanas"
]

BLACKLIST_KEYWORDS = [
    "record", "compilation", "highlights", "fail",
    "funny", "challenge", "extreme", "competition",
    "prank", "try not to laugh", "fails", "funniest",
    "moments", "best of", "worst of", "react"
]

WORKOUT_TYPES = {
    'cardio': {
        'beginner': ['Low Impact HIIT', 'Walking Workout', 'Beginner Dance'],
        'intermediate': ['HIIT', 'Tabata', 'Kickboxing'],
        'advanced': ['Advanced HIIT', 'Plyometrics', 'Sprint Intervals']
    },
    'strength': {
        'beginner': ['Bodyweight Basics', 'Light Dumbbells', 'Resistance Bands'],
        'intermediate': ['Full Body Dumbbell', 'Upper/Lower Split', 'Circuit Training'],
        'advanced': ['Heavy Lifting', 'Powerlifting', 'Advanced Calisthenics']
    },
    'flexibility': {
        'beginner': ['Gentle Stretching', 'Beginner Yoga'],
        'intermediate': ['Vinyasa Yoga', 'Mobility Drills'],
        'advanced': ['Advanced Yoga', 'Contortion', 'Deep Stretching']
    }
}