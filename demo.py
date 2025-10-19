#!/usr/bin/env python3
"""
Example usage of the Timeslot Scheduler with real student names and constraints
"""

from main import TimeslotScheduler

def demo_with_constraints():
    """Demonstrate the scheduler with student constraints"""
    
    # Sample student names
    student_names = [
        "Alice Johnson", "Bob Smith", "Carol Williams", "David Brown", "Emma Davis",
        "Frank Miller", "Grace Wilson", "Henry Moore", "Ivy Taylor", "Jack Anderson",
        "Kate Thomas", "Liam Jackson", "Mia White", "Noah Harris", "Olivia Martin",
        "Paul Thompson", "Quinn Garcia", "Ruby Martinez", "Sam Robinson", "Tina Clark",
        "Uma Rodriguez", "Victor Lewis", "Wendy Lee", "Xander Walker", "Yara Hall",
        "Zoe Allen", "Alex Young", "Beth King", "Carl Wright", "Diana Lopez",
        "Eric Hill", "Fiona Green", "George Adams", "Hannah Baker", "Ian Gonzalez",
        "Julia Nelson", "Kevin Carter"
    ]
    
    # Create scheduler
    scheduler = TimeslotScheduler(
        total_students=37,
        days=[1, 2],
        daily_start_hour=9,
        daily_end_hour=16,
        slot_duration_minutes=10,
        break_duration_minutes=0
    )
    
    # Generate schedule with constraints
    print("Generating presentation schedule with student constraints...")
    schedule = scheduler.generate_schedule(
        student_names=student_names,
        constraints_file="student_constraints.txt"
    )
    
    # Print summary
    scheduler.print_schedule_summary()
    
    # Export to CSV
    scheduler.export_to_csv("presentation_schedule_with_names.csv")
    
    print("\n=== CONSTRAINT ANALYSIS ===")
    constrained_students = list(scheduler.student_constraints.keys())
    print(f"Students with constraints: {len(constrained_students)}")
    for name in constrained_students:
        constraint = scheduler.student_constraints[name]
        print(f"  {name}:")
        if constraint.available_days:
            print(f"    Available days: {constraint.available_days}")
        if constraint.available_hours:
            hours_str = "; ".join([f"{start.strftime('%H:%M')}-{end.strftime('%H:%M')}" 
                                 for start, end in constraint.available_hours])
            print(f"    Available hours: {hours_str}")

if __name__ == "__main__":
    demo_with_constraints()