#!/usr/bin/env python3
"""
Advanced examples for the Timeslot Scheduler
"""

from main import IntervalTimeslotScheduler, TimeslotScheduler
import datetime

def demo_multiple_intervals():
    """Demonstrate scheduler with multiple time intervals per day"""
    print("=== DEMO: Multiple Intervals Per Day ===\n")
    
    # Configuration with complex schedule
    day_schedules = {
        1: [  # Day 1: Morning and afternoon sessions
            (datetime.time(9, 0), datetime.time(12, 0)),    # 9:00-12:00
            (datetime.time(13, 0), datetime.time(16, 0))    # 13:00-16:00
        ],
        2: [  # Day 2: Morning, short afternoon, evening
            (datetime.time(8, 30), datetime.time(11, 30)),  # 8:30-11:30
            (datetime.time(14, 0), datetime.time(15, 30)),  # 14:00-15:30
            (datetime.time(17, 0), datetime.time(19, 0))    # 17:00-19:00
        ],
        3: [  # Day 3: Extended day with breaks
            (datetime.time(9, 0), datetime.time(10, 30)),   # 9:00-10:30
            (datetime.time(11, 0), datetime.time(12, 30)),  # 11:00-12:30 (after coffee break)
            (datetime.time(13, 30), datetime.time(17, 0))   # 13:30-17:00 (after lunch)
        ]
    }
    
    scheduler = IntervalTimeslotScheduler(
        total_students=25,
        days=[1, 2, 3],
        day_schedules=day_schedules,
        slot_duration_minutes=15,  # 15-minute presentations
        break_duration_minutes=5   # 5-minute breaks between
    )
    
    # Generate schedule
    schedule = scheduler.generate_schedule()
    
    # Print summary
    scheduler.print_schedule_summary()
    
    # Export
    scheduler.export_to_csv("advanced_schedule.csv")
    
    print(f"\nTotal slots available: {len(scheduler.generate_all_possible_slots())}")

def demo_capacity_planning():
    """Demonstrate capacity planning scenarios"""
    print("\n=== DEMO: Capacity Planning Scenarios ===\n")
    
    scenarios = [
        {
            "name": "Tight Schedule",
            "students": 50,
            "slot_minutes": 5,
            "days": [(datetime.time(9, 0), datetime.time(17, 0))] * 1  # 1 day, 8 hours
        },
        {
            "name": "Comfortable Schedule", 
            "students": 30,
            "slot_minutes": 20,
            "days": [(datetime.time(9, 0), datetime.time(17, 0))] * 2  # 2 days, 8 hours each
        },
        {
            "name": "Conference Style",
            "students": 80,
            "slot_minutes": 10,
            "days": [(datetime.time(8, 0), datetime.time(18, 0))] * 3  # 3 days, 10 hours each
        }
    ]
    
    for scenario in scenarios:
        print(f"--- {scenario['name']} ---")
        
        # Convert to day_schedules format
        day_schedules = {}
        for i, (start, end) in enumerate(scenario['days'], 1):
            # Handle lunch break automatically
            if start <= datetime.time(12, 0) and end >= datetime.time(13, 0):
                day_schedules[i] = [
                    (start, datetime.time(12, 0)),
                    (datetime.time(13, 0), end)
                ]
            else:
                day_schedules[i] = [(start, end)]
        
        scheduler = IntervalTimeslotScheduler(
            total_students=scenario['students'],
            days=list(day_schedules.keys()),
            day_schedules=day_schedules,
            slot_duration_minutes=scenario['slot_minutes'],
            break_duration_minutes=0
        )
        
        total_slots = len(scheduler.generate_all_possible_slots())
        
        print(f"  Students: {scenario['students']}")
        print(f"  Slot duration: {scenario['slot_minutes']} minutes")
        print(f"  Available slots: {total_slots}")
        
        if scenario['students'] <= total_slots:
            print(f"  ✅ Status: {total_slots - scenario['students']} extra slots")
        else:
            shortage = scenario['students'] - total_slots
            print(f"  ❌ Status: {shortage} students can't be scheduled")
        print()

def demo_real_world_example():
    """Demonstrate a real-world university presentation schedule"""
    print("=== DEMO: University Final Presentations ===\n")
    
    # Real student names for the demo
    student_names = [
        "Emma Johnson", "Liam Smith", "Olivia Brown", "Noah Davis", "Ava Wilson",
        "William Moore", "Sophia Taylor", "James Anderson", "Isabella Thomas", "Benjamin Jackson",
        "Mia White", "Lucas Harris", "Charlotte Martin", "Henry Thompson", "Amelia Garcia",
        "Alexander Martinez", "Harper Robinson", "Michael Clark", "Evelyn Rodriguez", "Daniel Lewis",
        "Abigail Lee", "Matthew Walker", "Emily Hall", "Joseph Allen", "Elizabeth Young",
        "David King", "Sofia Wright", "Samuel Lopez", "Avery Hill", "Jackson Green"
    ]
    
    # Schedule: 3 days with different patterns
    day_schedules = {
        1: [  # Monday: Standard schedule
            (datetime.time(9, 0), datetime.time(12, 0)),
            (datetime.time(13, 0), datetime.time(16, 0))
        ],
        2: [  # Tuesday: Extended day
            (datetime.time(8, 30), datetime.time(12, 0)), 
            (datetime.time(13, 0), datetime.time(17, 30))
        ],
        3: [  # Wednesday: Half day
            (datetime.time(9, 0), datetime.time(13, 0))  # No afternoon (faculty meeting)
        ]
    }
    
    scheduler = IntervalTimeslotScheduler(
        total_students=30,
        days=[1, 2, 3],
        day_schedules=day_schedules,
        slot_duration_minutes=12,  # 12-minute presentations + questions
        break_duration_minutes=3   # 3-minute buffer between presentations
    )
    
    # Generate with constraints
    schedule = scheduler.generate_schedule(
        student_names=student_names,
        constraints_file="student_constraints.txt"
    )
    
    scheduler.print_schedule_summary()
    scheduler.export_to_csv("university_presentations.csv")
    
    print(f"\nSchedule exported to university_presentations.csv")

if __name__ == "__main__":
    print("🎓 Advanced Timeslot Scheduler Demonstrations\n")
    
    # Run all demos
    demo_multiple_intervals()
    demo_capacity_planning() 
    demo_real_world_example()
    
    print("✅ All demonstrations completed!")
    print("📄 Generated files:")
    print("  - advanced_schedule.csv")
    print("  - university_presentations.csv")