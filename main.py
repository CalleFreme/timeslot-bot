#!/usr/bin/env python3
"""
Timeslot Scheduler for Student Presentations

This script generates a schedule that evenly distributes presentation time slots
across multiple days, considering student availability constraints.
"""

import csv
import datetime
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import os

@dataclass
class TimeSlot:
    """Represents a presentation time slot"""
    day: int
    start_time: datetime.time
    end_time: datetime.time
    student_name: Optional[str] = None
    
    def __str__(self):
        return f"Day {self.day}: {self.start_time.strftime('%H:%M')}-{self.end_time.strftime('%H:%M')}"

@dataclass
class StudentConstraint:
    """Represents a student's availability constraints"""
    name: str
    available_days: List[int] = None  # None means all days available
    available_hours: List[Tuple[datetime.time, datetime.time]] = None  # None means all hours available

class TimeslotScheduler:
    """Main scheduler class for generating presentation time slots"""
    
    def __init__(self, 
                 total_students: int,
                 days: List[int],
                 daily_start_hour: int,
                 daily_end_hour: int,
                 slot_duration_minutes: int = 10,
                 break_duration_minutes: int = 0):
        """
        Initialize the scheduler
        
        Args:
            total_students: Total number of students to schedule
            days: List of day numbers (e.g., [1, 2] for 2 days)
            daily_start_hour: Start hour for each day (24-hour format)
            daily_end_hour: End hour for each day (24-hour format)
            slot_duration_minutes: Duration of each presentation slot in minutes
            break_duration_minutes: Break duration between slots in minutes
        """
        self.total_students = total_students
        self.days = days
        self.daily_start_hour = daily_start_hour
        self.daily_end_hour = daily_end_hour
        self.slot_duration_minutes = slot_duration_minutes
        self.break_duration_minutes = break_duration_minutes
        self.student_constraints = {}
        self.time_slots = []
        
    def load_student_constraints(self, filename: str) -> None:
        """
        Load student constraints from a text file
        
        File format (one per line):
        StudentName,AvailableDays,AvailableHours
        Example:
        John Doe,1-2,09:00-12:00;14:00-16:00
        Jane Smith,2,10:00-15:00
        """
        if not os.path.exists(filename):
            print(f"Constraints file {filename} not found. All students will be available for all slots.")
            return
            
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                        
                    parts = line.split(',')
                    if len(parts) < 1:
                        continue
                        
                    name = parts[0].strip()
                    available_days = None
                    available_hours = None
                    
                    # Parse available days
                    if len(parts) > 1 and parts[1].strip():
                        day_str = parts[1].strip()
                        if '-' in day_str:
                            start_day, end_day = map(int, day_str.split('-'))
                            available_days = list(range(start_day, end_day + 1))
                        else:
                            available_days = [int(day_str)]
                    
                    # Parse available hours
                    if len(parts) > 2 and parts[2].strip():
                        hour_ranges = []
                        for hour_range in parts[2].split(';'):
                            start_str, end_str = hour_range.split('-')
                            start_time = datetime.time.fromisoformat(start_str.strip())
                            end_time = datetime.time.fromisoformat(end_str.strip())
                            hour_ranges.append((start_time, end_time))
                        available_hours = hour_ranges
                    
                    self.student_constraints[name] = StudentConstraint(
                        name=name,
                        available_days=available_days,
                        available_hours=available_hours
                    )
                    
        except Exception as e:
            print(f"Error reading constraints file: {e}")
    
    def generate_all_possible_slots(self) -> List[TimeSlot]:
        """Generate all possible time slots for all days"""
        all_slots = []
        
        for day in self.days:
            current_time = datetime.time(self.daily_start_hour, 0)
            end_of_day = datetime.time(self.daily_end_hour, 0)
            
            while True:
                # Calculate slot end time
                current_datetime = datetime.datetime.combine(datetime.date.today(), current_time)
                slot_end_datetime = current_datetime + datetime.timedelta(minutes=self.slot_duration_minutes)
                slot_end_time = slot_end_datetime.time()
                
                # Check if slot fits within the day
                if slot_end_time > end_of_day:
                    break
                
                all_slots.append(TimeSlot(day=day, start_time=current_time, end_time=slot_end_time))
                
                # Move to next slot (including break)
                next_slot_datetime = slot_end_datetime + datetime.timedelta(minutes=self.break_duration_minutes)
                current_time = next_slot_datetime.time()
        
        return all_slots
    
    def is_student_available(self, student_name: str, slot: TimeSlot) -> bool:
        """Check if a student is available for a given time slot"""
        if student_name not in self.student_constraints:
            return True  # No constraints means always available
        
        constraint = self.student_constraints[student_name]
        
        # Check day availability
        if constraint.available_days and slot.day not in constraint.available_days:
            return False
        
        # Check time availability
        if constraint.available_hours:
            for start_time, end_time in constraint.available_hours:
                if start_time <= slot.start_time < end_time:
                    return True
            return False
        
        return True
    
    def assign_students_to_slots(self, student_names: List[str]) -> List[TimeSlot]:
        """Assign students to available time slots"""
        available_slots = self.generate_all_possible_slots()
        assigned_slots = []
        unassigned_students = student_names.copy()
        
        # First pass: assign students with constraints
        constrained_students = [name for name in student_names if name in self.student_constraints]
        for student_name in constrained_students:
            for slot in available_slots:
                if slot.student_name is None and self.is_student_available(student_name, slot):
                    slot.student_name = student_name
                    assigned_slots.append(slot)
                    unassigned_students.remove(student_name)
                    break
        
        # Second pass: assign remaining students to remaining slots
        for student_name in unassigned_students:
            for slot in available_slots:
                if slot.student_name is None:
                    slot.student_name = student_name
                    assigned_slots.append(slot)
                    break
        
        return assigned_slots
    
    def generate_schedule(self, student_names: List[str] = None, constraints_file: str = "student_constraints.txt") -> List[TimeSlot]:
        """
        Generate the complete schedule
        
        Args:
            student_names: List of student names. If None, generates generic names
            constraints_file: Path to student constraints file
        """
        # Load constraints
        self.load_student_constraints(constraints_file)
        
        # Generate student names if not provided
        if student_names is None:
            student_names = [f"Student_{i+1}" for i in range(self.total_students)]
        elif len(student_names) != self.total_students:
            print(f"Warning: Number of student names ({len(student_names)}) doesn't match total students ({self.total_students})")
            # Pad with generic names if needed
            while len(student_names) < self.total_students:
                student_names.append(f"Student_{len(student_names)+1}")
        
        # Generate schedule
        self.time_slots = self.assign_students_to_slots(student_names)
        
        return self.time_slots
    
    def export_to_csv(self, filename: str = "presentation_schedule.csv") -> None:
        """Export the schedule to a CSV file"""
        if not self.time_slots:
            print("No schedule generated yet. Please run generate_schedule() first.")
            return
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Day', 'Start Time', 'End Time', 'Student Name', 'Duration (minutes)']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for slot in self.time_slots:
                writer.writerow({
                    'Day': f"Day {slot.day}",
                    'Start Time': slot.start_time.strftime('%H:%M'),
                    'End Time': slot.end_time.strftime('%H:%M'),
                    'Student Name': slot.student_name or "AVAILABLE",
                    'Duration (minutes)': self.slot_duration_minutes
                })
        
        print(f"Schedule exported to {filename}")
    
    def print_schedule_summary(self) -> None:
        """Print a summary of the generated schedule"""
        if not self.time_slots:
            print("No schedule generated yet.")
            return
        
        print(f"\n=== PRESENTATION SCHEDULE SUMMARY ===")
        print(f"Total students: {self.total_students}")
        print(f"Total assigned slots: {len([s for s in self.time_slots if s.student_name])}")
        print(f"Slot duration: {self.slot_duration_minutes} minutes")
        
        for day in self.days:
            day_slots = [s for s in self.time_slots if s.day == day]
            print(f"\nDay {day}: {len(day_slots)} slots")
            for slot in day_slots:
                status = slot.student_name or "AVAILABLE"
                print(f"  {slot.start_time.strftime('%H:%M')}-{slot.end_time.strftime('%H:%M')}: {status}")
    
    def get_day_intervals_summary(self) -> str:
        """Get a summary of day intervals for display"""
        if hasattr(self, 'day_schedules'):
            summary = []
            for day in self.days:
                if day in self.day_schedules:
                    interval_strs = [f"{start.strftime('%H:%M')}-{end.strftime('%H:%M')}" 
                                   for start, end in self.day_schedules[day]]
                    summary.append(f"Day {day}: {', '.join(interval_strs)}")
            return "\n".join(summary)
        return f"Days {self.days}: {self.daily_start_hour:02d}:00-{self.daily_end_hour:02d}:00"

def get_user_input():
    """Get user input for scheduler configuration"""
    print("=== PRESENTATION TIMESLOT SCHEDULER ===\n")
    
    # Get number of students
    while True:
        try:
            total_students = int(input("Enter the number of students/slots needed: "))
            if total_students > 0:
                break
            else:
                print("Please enter a positive number.")
        except ValueError:
            print("Please enter a valid number.")
    
    # Get slot duration
    while True:
        try:
            slot_duration = int(input("Enter maximum time per slot (in minutes): "))
            if slot_duration > 0:
                break
            else:
                print("Please enter a positive number.")
        except ValueError:
            print("Please enter a valid number.")
    
    # Get break duration
    while True:
        try:
            break_duration = int(input("Enter break time between slots (in minutes, 0 for no breaks): "))
            if break_duration >= 0:
                break
            else:
                print("Please enter a non-negative number.")
        except ValueError:
            print("Please enter a valid number.")
    
    # Get number of days
    while True:
        try:
            num_days = int(input("Enter the number of days for presentations: "))
            if num_days > 0:
                break
            else:
                print("Please enter a positive number.")
        except ValueError:
            print("Please enter a valid number.")
    
    days = list(range(1, num_days + 1))
    day_schedules = {}
    
    # Get schedule for each day
    for day in days:
        print(f"\n--- Day {day} Configuration ---")
        print("Enter time intervals for this day:")
        print("  Flexible formats: 9-16, 09:00-16:00, 9:00-12:00,13:00-16:00")
        print("  Multiple intervals: separate with commas")
        print("  Note: Lunch breaks (12:00-13:00) will be automatically handled")
        
        while True:
            try:
                intervals_input = input(f"Day {day} time intervals: ")
                intervals = parse_time_intervals(intervals_input)
                if intervals:
                    day_schedules[day] = intervals
                    break
                else:
                    print("Please enter valid time intervals.")
            except Exception as e:
                print(f"Error parsing intervals: {e}. Please try again.")
    
    return total_students, slot_duration, break_duration, days, day_schedules

def normalize_time_string(time_str):
    """Normalize time string to HH:MM format"""
    time_str = time_str.strip()
    
    # Handle formats like "9", "09", "9:00", "09:00"
    if ':' not in time_str:
        # Just hour provided
        hour = int(time_str)
        return f"{hour:02d}:00"
    else:
        # Hour:minute format
        parts = time_str.split(':')
        if len(parts) == 2:
            hour = int(parts[0])
            minute = int(parts[1])
            return f"{hour:02d}:{minute:02d}"
    
    return time_str

def parse_time_intervals(intervals_str):
    """Parse time intervals string into list of (start, end) tuples"""
    intervals = []
    
    # Split by comma for multiple intervals
    interval_parts = [part.strip() for part in intervals_str.split(',')]
    
    for part in interval_parts:
        if '-' not in part:
            raise ValueError("Each interval must contain a hyphen (e.g., 09:00-12:00 or 9-16)")
        
        start_str, end_str = part.split('-')
        
        # Normalize time strings
        start_str = normalize_time_string(start_str.strip())
        end_str = normalize_time_string(end_str.strip())
        
        start_time = datetime.time.fromisoformat(start_str)
        end_time = datetime.time.fromisoformat(end_str)
        
        if start_time >= end_time:
            raise ValueError("Start time must be before end time")
        
        # Handle lunch break automatically - split intervals that cross 12:00-13:00
        lunch_start = datetime.time(12, 0)
        lunch_end = datetime.time(13, 0)
        
        if start_time < lunch_start and end_time > lunch_end:
            # Split into morning and afternoon sessions
            intervals.append((start_time, lunch_start))
            intervals.append((lunch_end, end_time))
            print(f"  ℹ️  Automatically split around lunch: {start_str}-{end_str} → {start_str}-12:00, 13:00-{end_str}")
        elif start_time < lunch_end and end_time > lunch_start:
            # Partially overlaps with lunch
            if start_time < lunch_start:
                intervals.append((start_time, lunch_start))
                print(f"  ℹ️  Adjusted for lunch break: {start_str}-{end_str} → {start_str}-12:00")
            if end_time > lunch_end:
                intervals.append((lunch_end, end_time))
                print(f"  ℹ️  Adjusted for lunch break: {start_str}-{end_str} → 13:00-{end_str}")
        else:
            # No lunch overlap
            intervals.append((start_time, end_time))
    
    return intervals

class IntervalTimeslotScheduler(TimeslotScheduler):
    """Extended scheduler that handles multiple time intervals per day"""
    
    def __init__(self, 
                 total_students: int,
                 days: List[int],
                 day_schedules: Dict[int, List[Tuple[datetime.time, datetime.time]]],
                 slot_duration_minutes: int = 10,
                 break_duration_minutes: int = 0):
        """
        Initialize the scheduler with flexible day schedules
        
        Args:
            total_students: Total number of students to schedule
            days: List of day numbers
            day_schedules: Dict mapping day numbers to list of (start_time, end_time) tuples
            slot_duration_minutes: Duration of each presentation slot in minutes
            break_duration_minutes: Break duration between slots in minutes
        """
        # Initialize parent class with dummy values
        super().__init__(total_students, days, 9, 17, slot_duration_minutes, break_duration_minutes)
        self.day_schedules = day_schedules
    
    def generate_all_possible_slots(self) -> List[TimeSlot]:
        """Generate all possible time slots for all days with flexible intervals"""
        all_slots = []
        
        for day in self.days:
            if day not in self.day_schedules:
                continue
                
            for start_time, end_time in self.day_schedules[day]:
                current_time = start_time
                
                while True:
                    # Calculate slot end time
                    current_datetime = datetime.datetime.combine(datetime.date.today(), current_time)
                    slot_end_datetime = current_datetime + datetime.timedelta(minutes=self.slot_duration_minutes)
                    slot_end_time = slot_end_datetime.time()
                    
                    # Check if slot fits within the current interval
                    if slot_end_time > end_time:
                        break
                    
                    all_slots.append(TimeSlot(day=day, start_time=current_time, end_time=slot_end_time))
                    
                    # Move to next slot (including break)
                    next_slot_datetime = slot_end_datetime + datetime.timedelta(minutes=self.break_duration_minutes)
                    current_time = next_slot_datetime.time()
        
        return all_slots

def interactive_main():
    """Interactive main function with user input"""
    total_students, slot_duration, break_duration, days, day_schedules = get_user_input()
    
    # Create scheduler with flexible intervals
    scheduler = IntervalTimeslotScheduler(
        total_students=total_students,
        days=days,
        day_schedules=day_schedules,
        slot_duration_minutes=slot_duration,
        break_duration_minutes=break_duration
    )
    
    # Show configuration summary
    print(f"\n=== CONFIGURATION SUMMARY ===")
    print(f"Total students: {total_students}")
    print(f"Slot duration: {slot_duration} minutes")
    print(f"Break duration: {break_duration} minutes")
    print(f"Days and schedules:")
    for day, intervals in day_schedules.items():
        interval_strs = [f"{start.strftime('%H:%M')}-{end.strftime('%H:%M')}" for start, end in intervals]
        print(f"  Day {day}: {', '.join(interval_strs)}")
    
    # Calculate total available slots
    total_available_slots = len(scheduler.generate_all_possible_slots())
    print(f"Total available slots: {total_available_slots}")
    
    if total_students > total_available_slots:
        print(f"\n❌ WARNING: Not enough slots available!")
        print(f"   Need: {total_students} slots")
        print(f"   Have: {total_available_slots} slots")
        print(f"   Shortage: {total_students - total_available_slots} slots")
        print("\nSuggestions:")
        print("- Reduce presentation time per student")
        print("- Add more time intervals")
        print("- Add more days")
        
        proceed = input("\nDo you want to proceed anyway? (y/N): ").lower().strip()
        if proceed != 'y':
            print("Scheduler cancelled.")
            return
    else:
        print(f"✅ Sufficient capacity: {total_available_slots - total_students} extra slots available")
    
    # Generate the schedule
    print(f"\nGenerating presentation schedule...")
    schedule = scheduler.generate_schedule()
    
    # Print summary
    scheduler.print_schedule_summary()
    
    # Export to CSV
    filename = input("\nEnter CSV filename (press Enter for 'presentation_schedule.csv'): ").strip()
    if not filename:
        filename = "presentation_schedule.csv"
    if not filename.endswith('.csv'):
        filename += '.csv'
    
    scheduler.export_to_csv(filename)
    
    print(f"\n✅ Schedule successfully generated and exported to {filename}")

def main():
    """Main function - choose between interactive and example mode"""
    print("Choose mode:")
    print("1. Interactive mode (user input)")
    print("2. Example mode (preset configuration)")
    
    while True:
        choice = input("Enter choice (1 or 2): ").strip()
        if choice == '1':
            interactive_main()
            break
        elif choice == '2':
            example_main()
            break
        else:
            print("Please enter 1 or 2.")

def example_main():
    """Example main function with preset configuration"""
    # Example configuration based on the original requirements
    scheduler = TimeslotScheduler(
        total_students=37,
        days=[1, 2],  # 2 days
        daily_start_hour=9,  # 09:00
        daily_end_hour=16,   # 16:00
        slot_duration_minutes=10,  # 10 minutes per presentation
        break_duration_minutes=0   # No breaks between presentations
    )
    
    # Generate the schedule
    print("Generating presentation schedule...")
    schedule = scheduler.generate_schedule()
    
    # Print summary
    scheduler.print_schedule_summary()
    
    # Export to CSV
    scheduler.export_to_csv("presentation_schedule.csv")
    
    # Check if all students could be scheduled
    total_available_slots = len(scheduler.generate_all_possible_slots())
    print(f"\nTotal available slots: {total_available_slots}")
    
    if scheduler.total_students > total_available_slots:
        print(f"WARNING: Not enough slots available! {scheduler.total_students - total_available_slots} students couldn't be scheduled.")
        print("Consider:")
        print("- Reducing presentation time per student")
        print("- Adding more days")
        print("- Extending daily hours")

if __name__ == "__main__":
    main()