"""
main.py - Testing script to verify PawPal+ scheduling logic.

This script creates sample owners, pets, and tasks, then generates
and displays a daily schedule to verify the core logic works.
"""

from pawpal_system import Owner, Pet, CareTask, Scheduler


def main():
    # Create owner with 120 minutes available in their day
    owner = Owner(
        name="Jordan",
        daily_time_available=120,
        preferences={"preferred_time": "morning"}
    )
    
    # Create two pets
    dog = Pet(
        name="Mochi",
        species="dog",
        age=3,
        notes="High energy, needs lots of activity"
    )
    
    cat = Pet(
        name="Luna",
        species="cat",
        age=5,
        notes="Indoor cat, enjoys quiet time"
    )
    
    # Add dog to owner
    owner.add_pet(dog)
    owner.add_pet(cat)
    
    # Create tasks for the dog
    dog_tasks = [
        CareTask(
            title="Morning walk",
            category="exercise",
            duration_minutes=20,
            priority="high",
            preferred_time="morning",
            required=True
        ),
        CareTask(
            title="Feeding",
            category="feeding",
            duration_minutes=10,
            priority="high",
            required=True
        ),
        CareTask(
            title="Playtime",
            category="enrichment",
            duration_minutes=30,
            priority="medium"
        ),
        CareTask(
            title="Grooming",
            category="grooming",
            duration_minutes=25,
            priority="low"
        )
    ]
    
    # Create tasks for the cat
    cat_tasks = [
        CareTask(
            title="Feeding",
            category="feeding",
            duration_minutes=10,
            priority="high",
            required=True
        ),
        CareTask(
            title="Litter box cleaning",
            category="hygiene",
            duration_minutes=5,
            priority="high",
            required=True
        ),
        CareTask(
            title="Interactive play",
            category="enrichment",
            duration_minutes=15,
            priority="medium"
        )
    ]
    
    # Add tasks to pets
    for task in dog_tasks:
        dog.add_task(task)
    
    for task in cat_tasks:
        cat.add_task(task)
    
    # Create scheduler and generate plans
    scheduler = Scheduler(start_hour=8)
    
    print("=" * 60)
    print("PawPal+ - Today's Schedule")
    print("=" * 60)
    print(f"\nOwner: {owner.name}")
    print(f"Available time: {owner.daily_time_available} minutes")
    print(f"Preferences: {owner.preferences}\n")
    
    # Generate plan for each pet
    for pet in owner.get_pets():
        print(f"\n{'─' * 60}")
        print(f"Pet: {pet.name} ({pet.species.capitalize()})")
        print(f"Tasks available: {len(pet.get_tasks())}")
        print(f"{'─' * 60}")
        
        plan = scheduler.generate_plan(owner, pet, pet.get_tasks())
        
        # Display scheduled items
        if plan.items:
            print("\nScheduled Tasks:")
            for i, item in enumerate(plan.items, 1):
                print(
                    f"  {i}. [{item.start_time}-{item.end_time}] {item.task.title} "
                    f"({item.task.duration_minutes} min) — {item.reason}"
                )
        else:
            print("\nNo tasks scheduled.")
        
        # Display skipped tasks
        if plan.skipped_tasks:
            print(f"\nSkipped Tasks ({len(plan.skipped_tasks)}):")
            for task in plan.skipped_tasks:
                print(
                    f"  • {task.title} ({task.duration_minutes} min, {task.priority} priority)"
                )
        
        # Display plan summary
        print(f"\nTime Used: {plan.available_minutes - plan.remaining_minutes()} / "
              f"{plan.available_minutes} minutes")
        print(f"Time Remaining: {plan.remaining_minutes()} minutes")
        print(f"Plan Valid: {plan.is_valid_plan()}")
    
    print(f"\n{'=' * 60}\n")


if __name__ == "__main__":
    main()
