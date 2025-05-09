# Hunting Calendar Generator

## Overview
This Python script generates an iCalendar (.ics) file from CSV data containing hunting season information. The calendar includes events for each hunting season with detailed information about the species, areas, and bag limits.

## Requirements
- Python 3.6+
- Required Python packages:
    - `icalendar`
    - `pytz`
    - `csv` (standard library)
    - `argparse` (standard library)
    - `datetime` (standard library)

You can install the required packages using pip:
```
pip install icalendar pytz
```

## CSV Format
The input CSV file must contain the following columns:

| Column Name | Description | Example Values |
|-------------|-------------|----------------|
| Species | Animal species name | Deer, Turkey, Squirrel |
| Scope | Optional subcategory of the species | Archery, Youth Gun, Roosters Only |
| Area | Geographic hunting area | Statewide, 17 Counties, Lake Erie Marsh Zone |
| Opening Date | Season start date (MM/DD/YY) | 09/27/25 |
| Closing Date | Season end date (MM/DD/YY) | 02/01/26 |
| Days Of Week | Days when hunting is allowed | ALL, F:SA:SU (Friday, Saturday, Sunday) |
| Limit | Bag limit information | 4/Day, 1/Season, See Bag Limit Map |

### Days Of Week Format
- `ALL`: Hunting allowed every day of the week
- Individual days are specified with a colon-separated list:
    - `M`: Monday
    - `TU`: Tuesday
    - `W`: Wednesday
    - `TH`: Thursday
    - `F`: Friday
    - `SA`: Saturday
    - `SU`: Sunday
- Example: `F:SA:SU` means hunting is allowed only on Friday, Saturday, and Sunday

## Usage

### Basic Usage
```
python csv2ical.py input_file.csv
```

This will generate a file named `hunting_calendar.ics` in the current directory.

### Specifying Output File
```
python csv2ical.py input_file.csv --output my_calendar.ics
```

This will generate a file named `my_calendar.ics`.

## Output
The script generates an iCalendar (.ics) file with events representing hunting seasons. The events include:

- **Summary**: Number of species available on that date
- **Description**: Detailed information about each species, including:
    - Species name
    - Scope (if applicable)
    - Area(s)
    - Bag limit

The description has the format:
```
Species1 (Scope1: Area1, Area2 | Scope2: Area1): Bag Limit
Species2 (Scope1: Area1, Area2 | Scope2: Area1): Bag Limit
```

If the bag limit is different for a species, it will be shown separately.
For example, in Ohio on January 9th 2026 you can trap river otter in zone a at a different bag limit than in zone b. The calendar will show:
```
River Otter (Trapping: Zone A): 3/Season
River Otter (Trapping: Zone B): 1/Season
```
However, if you were in a fantasy state where the bag limit was the same for both zones, it would show:
```
River Otter (Trapping: Zone A, Zone B): 3/Season
```

If there is no scope, the species will just show the area:
```
River Otter (Statewide): 3/Season
```

## Calendar Integration
The generated .ics file can be imported into most calendar applications:

- **Google Calendar**: In the web interface, go to Settings > Import & Export > Import
- **Microsoft Outlook**: File > Open & Export > Import/Export > Import an iCalendar (.ics) file
- **Apple Calendar**: File > Import
- **Mobile devices**: You can usually email the .ics file to yourself and open it to add it to your calendar

## Example CSV Entry
```csv
Species,Scope,Area,Opening Date,Closing Date,Days Of Week,Limit
Deer,Archery,Statewide,09/27/25,02/01/26,ALL,See Bag Limit Map
Turkey,Fall,Statewide,10/01/25,10/26/25,ALL,1/Season
Crow,,Statewide,06/06/25,03/01/26,F:SA:SU,None
```

## Features
- Automatically groups consecutive days with identical hunting options
- Organizes species by scope and area
- Properly handles date ranges and day-of-week restrictions
- Creates calendar events with detailed descriptions for each hunting opportunity

## Example Output
When you import the calendar, each day will show what can be hunted on that day. For example, a calendar event might look like:

```
3 Species

Deer (Archery: Statewide): See Bag Limit Map

Squirrel (Statewide): 6/Day

Turkey (Fall: Statewide): 1/Season
```