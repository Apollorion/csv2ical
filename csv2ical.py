import csv
import argparse
from datetime import datetime, timedelta
from icalendar import Calendar, Event
import pytz
import sys

# Set up command line arguments
parser = argparse.ArgumentParser(description='Generate hunting calendar from CSV data')
parser.add_argument('input_file', help='Path to the CSV file containing hunting seasons data')
parser.add_argument('--output', default='hunting_calendar.ics', help='Output iCalendar file (default: hunting_calendar.ics)')
args = parser.parse_args()

# Read the CSV data from file
try:
    with open(args.input_file, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        seasons = list(reader)
except FileNotFoundError:
    print(f"Error: Could not find the file {args.input_file}")
    sys.exit(1)
except Exception as e:
    print(f"Error reading CSV file: {e}")
    sys.exit(1)

# Process day of week information
def is_day_allowed(day_of_week, days_of_week):
    if days_of_week == "ALL":
        return True
    days_map = {
        "M": 0,  # Monday
        "TU": 1, # Tuesday
        "W": 2,  # Wednesday
        "TH": 3, # Thursday
        "F": 4,  # Friday
        "SA": 5, # Saturday
        "SU": 6  # Sunday
    }
    allowed_days = days_of_week.split(":")
    return any(day_of_week == days_map[day] for day in allowed_days)

# Create date range from beginning of first season to end of last season
def parse_date(date_str):
    return datetime.strptime(date_str, "%m/%d/%y").date()

# Find the earliest and latest dates
min_date = min(parse_date(season["Opening Date"]) for season in seasons)
max_date = max(parse_date(season["Closing Date"]) for season in seasons)

# Create a dictionary to store huntable species for each date
hunting_calendar = {}

# For each date in the range
current_date = min_date
while current_date <= max_date:
    # For each date, check what can be hunted
    huntable_species = []

    for season in seasons:
        opening_date = parse_date(season["Opening Date"])
        closing_date = parse_date(season["Closing Date"])

        # Check if the current date is within the season
        if opening_date <= current_date <= closing_date:
            # Check day of week restrictions
            day_of_week = current_date.weekday()
            days_of_week = season["Days Of Week"]

            if days_of_week == "ALL" or is_day_allowed(day_of_week, days_of_week):
                # Format the species information
                species_info = f"{season['Species']}"
                if season["Scope"]:
                    species_info += f" ({season['Scope']})"
                species_info += f" - {season['Area']}"
                species_info += f" - Limit: {season['Limit']}"

                huntable_species.append(species_info)

    # Only add an entry if there are huntable species on this day
    if huntable_species:
        hunting_calendar[current_date] = huntable_species

    # Move to next day
    current_date += timedelta(days=1)

# Create iCalendar
cal = Calendar()
cal.add('prodid', '-//Hunting Calendar//EN')
cal.add('version', '2.0')

# Helper function to find consecutive days with the same hunting options
def find_consecutive_days(start_date, hunting_calendar):
    current_date = start_date
    end_date = start_date
    current_species = set(hunting_calendar[start_date])

    while True:
        next_date = end_date + timedelta(days=1)
        if next_date in hunting_calendar and set(hunting_calendar[next_date]) == current_species:
            end_date = next_date
        else:
            break

    return end_date

# Create events for consecutive days with the same hunting options
processed_dates = set()
for date in sorted(hunting_calendar.keys()):
    if date in processed_dates:
        continue

    end_date = find_consecutive_days(date, hunting_calendar)

    # Mark all dates in this range as processed
    current = date
    while current <= end_date:
        processed_dates.add(current)
        current += timedelta(days=1)

    # Create event
    event = Event()

    # Group by species and limit, but keep scope-area pairs intact
    species_groups = {}
    for species_info in hunting_calendar[date]:
        parts = species_info.split(" - ")
        species_part = parts[0]  # This contains the species and scope
        area_part = parts[1]
        limit_part = parts[2]

        # Extract species and scope
        if "(" in species_part:
            species_name = species_part.split(" (")[0]
            scope = species_part.split(" (")[1][:-1]  # Remove the trailing ')'
        else:
            species_name = species_part
            scope = ""

        area = area_part
        limit = limit_part.replace("Limit: ", "")

        # Create a key that includes both species and limit
        key = (species_name, limit)

        # Add to the group
        if key not in species_groups:
            species_groups[key] = {
                "scope_area_pairs": set(),
                "limit": limit
            }

        # Keep scope and area together as a pair
        scope_area_pair = (scope, area)
        species_groups[key]["scope_area_pairs"].add(scope_area_pair)

    # Format the species information
    description_lines = []
    for (species, limit), info in species_groups.items():
        # Group by scope for better organization when multiple areas per scope
        scope_to_areas = {}
        for scope, area in info["scope_area_pairs"]:
            if scope not in scope_to_areas:
                scope_to_areas[scope] = set()
            scope_to_areas[scope].add(area)

        # Build the line with all scope-area combinations
        scope_area_texts = []
        for scope, areas in sorted(scope_to_areas.items()):
            areas_text = ", ".join(sorted(areas))
            if scope:
                scope_area_texts.append(f"{scope}: {areas_text}")
            else:
                scope_area_texts.append(areas_text)

        scope_area_combined = " | ".join(scope_area_texts)
        description_lines.append(f"{species} ({scope_area_combined}): {limit}")

    # Sort the description lines alphabetically by species
    description_lines.sort()

    # Count unique species (regardless of limit differences)
    unique_species = set(species for species, _ in species_groups.keys())

    event.add('summary', f"{len(unique_species)} Species")
    event.add('description', "\n\n".join(description_lines))

    # Add start date (use UTC for simplicity)
    event_start = datetime.combine(date, datetime.min.time())
    event_start = event_start.replace(tzinfo=pytz.UTC)
    event.add('dtstart', event_start.date())

    # Add end date (add 1 day because the end date is exclusive in iCalendar)
    event_end = datetime.combine(end_date + timedelta(days=1), datetime.min.time())
    event_end = event_end.replace(tzinfo=pytz.UTC)
    event.add('dtend', event_end.date())

    # Add event to calendar
    cal.add_component(event)

# Write to file
try:
    with open(args.output, 'wb') as f:
        f.write(cal.to_ical())
    print(f"Calendar created successfully as '{args.output}'")
except Exception as e:
    print(f"Error writing calendar file: {e}")
    sys.exit(1)