# Timeslot Scheduler for Student Presentations

## Purpose

This Python script generates an optimized schedule for student presentations, evenly distributing time slots across multiple days while respecting individual student availability constraints. The script features **interactive user input** and **flexible time interval management**.

## Features

- 🎯 **Interactive Configuration**: User-friendly prompts for all settings
- ⏰ **Flexible Time Management**: Multiple time intervals per day with automatic lunch break handling
- 👥 **Student Constraints**: Handle students who can only present during specific times or days
- 📊 **Even Distribution**: Automatically distributes students across available time slots
- 📄 **CSV Export**: Generates ready-to-use CSV files for scheduling
- ⚡ **Conflict Resolution**: Prioritizes students with constraints first, then fills remaining slots
- 📈 **Capacity Planning**: Automatic warnings when insufficient slots are available
- 🔧 **Multiple Modes**: Interactive mode and preset example mode

## Requirements

- Python 3.6 or higher
- No external dependencies (uses only standard library)

## Quick Start

### Interactive Mode (Recommended)

Run the script and follow the prompts:

```bash
python main.py
# Choose option 1 for interactive mode
```

The script will ask for:
1. **Number of students** (e.g., 37)
2. **Slot duration** (e.g., 10 minutes)
3. **Break time** between slots (e.g., 0 minutes)
4. **Number of days** (e.g., 2)
5. **Time intervals for each day** (flexible format)

### Example Interactive Session

```
Enter the number of students/slots needed: 37
Enter maximum time per slot (in minutes): 10
Enter break time between slots (in minutes, 0 for no breaks): 0
Enter the number of days for presentations: 2

--- Day 1 Configuration ---
Day 1 time intervals: 9-16
ℹ️ Automatically split around lunch: 09:00-16:00 → 09:00-12:00, 13:00-16:00

--- Day 2 Configuration ---  
Day 2 time intervals: 8:30-11:30,14-17
```

### Time Format Flexibility

The script accepts various time formats:
- `9-16` → 09:00-16:00 (auto lunch split)
- `09:00-16:00` → Full format
- `9:00-12:00,13:00-16:00` → Multiple intervals
- Automatic lunch break handling (12:00-13:00)

### Custom Configuration

Modify the `main()` function in `main.py` to customize:

```python
scheduler = TimeslotScheduler(
    total_students=37,              # Number of students
    days=[1, 2],                    # Day numbers (e.g., [1, 2, 3] for 3 days)
    daily_start_hour=9,             # Start time (24-hour format)
    daily_end_hour=16,              # End time (24-hour format)
    slot_duration_minutes=10,       # Minutes per presentation
    break_duration_minutes=0        # Minutes between presentations
)
```

### Student Constraints File

Create a `student_constraints.txt` file to specify when students are available:

```
# Format: StudentName,AvailableDays,AvailableHours
John Doe,1,09:00-12:00              # Only Day 1, morning only
Jane Smith,2,10:00-15:00            # Only Day 2, 10 AM to 3 PM
Bob Johnson,,09:00-11:00;13:00-16:00 # Both days, morning and afternoon
Alice Brown,1-2,14:00-16:00         # Both days, afternoon only
Mike Wilson,1,                      # Only Day 1, any time
Sarah Davis,,09:00-10:00            # Both days, 9-10 AM only
```

#### Constraint Format Rules:

- **StudentName**: Exact name of the student
- **AvailableDays**: 
  - Single day: `1` or `2`
  - Range: `1-2` (both days)
  - Empty: All days available
- **AvailableHours**:
  - Single range: `09:00-12:00`
  - Multiple ranges: `09:00-12:00;14:00-16:00`
  - Empty: All hours available

## Output

The script generates:

1. **Console Summary**: Overview of the schedule with slot assignments
2. **CSV File**: `presentation_schedule.csv` with columns:
   - Day
   - Start Time
   - End Time
   - Student Name
   - Duration (minutes)

## Example Output

```
=== PRESENTATION SCHEDULE SUMMARY ===
Total students: 37
Total assigned slots: 37
Slot duration: 10 minutes

Day 1: 21 slots
  09:00-09:10: John Doe
  09:10-09:20: Mike Wilson
  09:20-09:30: Student_3
  ...

Day 2: 21 slots
  09:00-09:10: Jane Smith
  09:10-09:20: Student_4
  ...

Total available slots: 42
Schedule exported to presentation_schedule.csv
```

## Capacity Planning

The script automatically calculates available slots:

- **Formula**: `(daily_hours * 60 / slot_duration) * number_of_days`
- **Example**: `(7 hours * 60 minutes / 10 minutes) * 2 days = 84 slots`

If you have more students than available slots, the script will warn you and suggest:
- Reducing presentation time per student
- Adding more presentation days
- Extending daily hours

## Scheduling Algorithm

1. **Generate Time Slots**: Creates all possible slots within specified hours
2. **Priority Assignment**: Students with constraints are scheduled first
3. **Fill Remaining**: Unconstrained students fill remaining available slots
4. **Conflict Resolution**: If conflicts arise, constrained students take priority

## Troubleshooting

### Common Issues

1. **Not enough slots**: Increase daily hours, add days, or reduce slot duration
2. **Constraints file not found**: Ensure `student_constraints.txt` exists in the same directory
3. **Invalid time format**: Use HH:MM format (e.g., 09:00, not 9:00 AM)

### File Format Errors

- Lines starting with `#` are treated as comments
- Empty lines are ignored
- Malformed lines are skipped with a warning

## Customization Examples

### Short Presentations (5 minutes each)
```python
scheduler = TimeslotScheduler(
    total_students=50,
    days=[1],
    daily_start_hour=9,
    daily_end_hour=17,
    slot_duration_minutes=5,
    break_duration_minutes=1  # 1-minute buffer
)
```

### Multi-day Conference (3 days)
```python
scheduler = TimeslotScheduler(
    total_students=100,
    days=[1, 2, 3],
    daily_start_hour=8,
    daily_end_hour=18,
    slot_duration_minutes=15,
    break_duration_minutes=5
)
```

### Extended Hours with Lunch Break
For lunch breaks, modify the daily hours or create separate morning/afternoon sessions:

```python
# Morning session
morning_scheduler = TimeslotScheduler(
    total_students=20,
    days=[1, 2],
    daily_start_hour=9,
    daily_end_hour=12,  # End at noon
    slot_duration_minutes=10
)

# Afternoon session  
afternoon_scheduler = TimeslotScheduler(
    total_students=17,
    days=[1, 2], 
    daily_start_hour=13,  # Start after lunch
    daily_end_hour=16,
    slot_duration_minutes=10
)
```

## License

This script is provided as-is for educational and organizational use. Feel free to modify according to your needs.