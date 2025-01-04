#!/usr/bin/env python3
from datetime import datetime, timedelta
from termcolor import colored
from typing import List, Dict
import sys
import random

class TimewarVisualizer:
    def __init__(self):
        self.tag_colors = {
            'work': 'blue',
            'meeting': 'green',
            'coding': 'yellow',
            'break': 'red',
        }
    
    def get_color_for_tag(self, tag: str):
        """Get color name for a tag, defaulting to white if not found"""
        return self.tag_colors.get(tag.lower(), 'white')
        
    def create_tag_label(self, tag: str, fg_color: str = 'white', bg_color: str = 'blue', width: int = None) -> str:
        """Create a colored tag label with background, optionally fixed width"""
        label = tag
        if width is not None:
            # Truncate or pad to fit width
            if len(label) > width:
                label = label[:width]
            else:
                label = label.ljust(width)
        # Add space after label for better readability
        label = f"{label} "
        return colored(label, fg_color, f"on_{bg_color}")
    
    def create_blocks(self, n: int, bg_color: str = 'blue', fg_color: str = 'red', char: str = '█') -> str:
        """Create a string of n colored blocks"""
        return colored(char * n, fg_color, f"on_{bg_color}")

    def create_styled_text(self, text: str, fg_color: str, bg_color: str, n: int = 1) -> str:
        """Create styled text with foreground and background colors.
        Shows text once followed by (n-1) empty colored blocks"""
        if n < 1:
            return ""
            
        # Create the text block
        styled = colored(f" {text} ", fg_color, f"on_{bg_color}")
        
        # Create empty blocks if needed
        if n > 1:
            empty = colored(" " * len(text), fg_color, f"on_{bg_color}")
            styled += empty * (n - 1)

        # shorten the string to n characters
        styled = styled[:n]
            
        return styled

    def get_hourly_blocks(self, events: List[Dict]) -> Dict[str, List[Dict]]:
        """Get tag blocks per hour with their duration in minutes"""
        hourly_data = {}
        
        for event in events:
            current_time = event['start']
            while current_time < event['end']:
                hour_key = current_time.strftime("%H:%M")
                if hour_key not in hourly_data:
                    hourly_data[hour_key] = []
                
                # Calculate duration in this hour
                end_of_hour = current_time.replace(minute=59, second=59, microsecond=999999)
                duration = min(event['end'], end_of_hour) - current_time
                duration_min = int(duration.total_seconds() / 60)
                
                hourly_data[hour_key].append({
                    'tag': event['tag'],
                    'duration': duration_min
                })
                
                # Move to next hour
                current_time = end_of_hour + timedelta(microseconds=1)
        
        return hourly_data

    def create_continuous_timeline(self, events: List[Dict]) -> None:
        """Create a continuous timeline with wrapping every 60 chars"""
        if not events:
            self.console.print("No events to display", style="red")
            return
            
        # Set static start time to 4 AM
        start_time = datetime.now().replace(hour=4, minute=0, second=0, microsecond=0)
        current_time = start_time
        end_time = datetime.now()
        
        timeline = []
        while current_time <= end_time:
            # Find active event at this minute
            active_event = next(
                (e for e in events if e['start'] <= current_time < e['end']),
                None
            )
            
            if active_event:
                color = self.get_color_for_tag(active_event['tag'])
                # Show tag text only at start of event, blocks for rest
                if current_time == active_event['start']:
                    char = colored(f" {active_event['tag']} ", "red", "on_blue")
                else:
                    char = colored("█", "red", "on_blue")
            else:
                char = colored("░", attrs=['dark'])
            
            timeline.append(char)
            
            # Print line every 60 chars
            if len(timeline) % 60 == 0:
                print(f"{''.join(timeline[-60:])}")
            
            current_time += timedelta(minutes=1)
        
        # Print any remaining chars
        if len(timeline) % 60 != 0:
            print(f"{''.join(timeline[-(len(timeline)%60):])}")

    def create_single_line_timeline(self, events: List[Dict]) -> str:
        """Create a single line timeline visualization using styled text"""
        if not events:
            return colored("No events", "red")
            
        # Find earliest start and latest end times
        start_time = min(e['start'] for e in events)
        end_time = max(e['end'] for e in events)
        total_minutes = int((end_time - start_time).total_seconds() / 60)
        
        timeline = []
        for event in events:
            # Calculate event duration in minutes
            duration = int((event['end'] - event['start']).total_seconds() / 60)
            
            # Get color for tag
            color = self.get_color_for_tag(event['tag'])
            
            # Create styled text for event
            styled = self.create_styled_text(
                event['tag'],
                fg_color='white',
                bg_color=color,
                n=duration
            )
            timeline.append(styled)
        
        return ''.join(timeline)

    def create_wrapped_timeline(self, events: List[Dict], wrap_at: int = 60) -> str:
        """Create a timeline visualization that wraps every wrap_at visible characters"""
        if not events:
            return colored("No events", "red")
            
        # Get the single line timeline
        timeline = self.create_single_line_timeline(events)
        
        # Split into chunks of wrap_at visible characters
        wrapped = []
        current_line = []
        visible_count = 0
        
        # Helper to detect ANSI escape sequences
        def is_ansi_escape(char):
            return char == '\x1b'
        
        # Helper to skip ANSI sequence
        def skip_ansi_sequence(timeline, i):
            while i < len(timeline) and timeline[i] != 'm':
                i += 1
            return i + 1  # Skip the 'm' too
        
        i = 0
        while i < len(timeline):
            if is_ansi_escape(timeline[i]):
                # Add the entire ANSI sequence to current line
                start = i
                i = skip_ansi_sequence(timeline, i)
                current_line.append(timeline[start:i])
            else:
                # Add visible character and count it
                current_line.append(timeline[i])
                visible_count += 1
                i += 1
                
                # Wrap if we've reached the limit
                if visible_count >= wrap_at:
                    # Pad with spaces if needed to reach exact width
                    # Need to add spaces with the same ANSI color as last character
                    last_color = ''.join([c for c in current_line if c.startswith('\x1b')][-1:]) if any(c.startswith('\x1b') for c in current_line) else ''
                    while visible_count < wrap_at:
                        if last_color:
                            current_line.append(last_color + ' ' + '\x1b[0m')
                        else:
                            current_line.append(' ')
                        visible_count += 1
                    wrapped.append(''.join(current_line))
                    current_line = []
                    visible_count = 0
        
        # Add any remaining characters
        if current_line:
            # Pad last line with spaces to reach exact width
            # Need to add spaces with the same ANSI color as last character
            last_color = ''.join([c for c in current_line if c.startswith('\x1b')][-1:]) if any(c.startswith('\x1b') for c in current_line) else ''
            while visible_count < wrap_at:
                if last_color:
                    current_line.append(last_color + ' ' + '\x1b[0m')
                else:
                    current_line.append(' ')
                visible_count += 1
            wrapped.append(''.join(current_line))
            
        return '\n'.join(wrapped)

    def create_timeline(self, events: List[Dict]) -> None:
        """Create and display a timeline visualization"""
        if not events:
            self.console.print("No events to display", style="red")
            return
            
        print("\nContinuous Timeline:")
        self.create_continuous_timeline(events)
        
        print("\nSingle Line Timeline:")
        print(self.create_single_line_timeline(events))
        
        print("\nHourly Breakdown:")
        # Set static start time to 4 AM
        start_time = datetime.now().replace(hour=4, minute=0, second=0, microsecond=0)
        current_hour = start_time
        end_time = events[-1]['end']
        
        while current_hour <= end_time:
            # Create the hour label
            hour_label = current_hour.strftime("%H:%M")
            
            # Create the timeline bar
            timeline = []
            for minute in range(60):
                time_point = current_hour + timedelta(minutes=minute)
                # Find active event at this minute
                active_event = next(
                    (e for e in events if e['start'] <= time_point < e['end']),
                    None
                )
                
                if active_event:
                    color = self.get_color_for_tag(active_event['tag'])
                    # Show tag text only at start of event, blocks for rest
                    if time_point == active_event['start']:
                        char = self.create_tag_label(
                            active_event['tag'], 
                            fg_color='white',
                            bg_color=color
                        )
                    else:
                        char = self.create_blocks(1, bg_color=color, fg_color='white')
                else:
                    char = self.create_blocks(1, bg_color='black', fg_color='white', char='░')
                
                timeline.append(char)
            
            # Print the hour line
            print(f"{colored(hour_label, attrs=['bold'])} {''.join(timeline)}")
            current_hour += timedelta(hours=1)

if __name__ == "__main__":
    # Demo tag labels
    visualizer = TimewarVisualizer()
    print("Tag Label Examples:")
    print(visualizer.create_tag_label('meeting', 'white', 'green', width=10))
    print(visualizer.create_tag_label('coding', 'black', 'yellow', width=10))
    print(visualizer.create_tag_label('break', 'white', 'red', width=10))
    print(visualizer.create_tag_label('work', 'white', 'blue', width=10))
    print()
    
    print("Fixed Width Examples:")
    print(visualizer.create_tag_label('verylongtagname', 'white', 'green', width=10))
    print(visualizer.create_tag_label('short', 'black', 'yellow', width=10))
    print()
    
    
    # Demo data
    demo_events = [
        {
            'start': datetime.now().replace(hour=9, minute=0),
            'end': datetime.now().replace(hour=10, minute=30),
            'tag': 'meeting',
            'label': 'Standup'
        },
        {
            'start': datetime.now().replace(hour=10, minute=30),
            'end': datetime.now().replace(hour=11, minute=0),
            'tag': 'break',
            'label': 'Coffee'
        },
        {
            'start': datetime.now().replace(hour=11, minute=0),
            'end': datetime.now().replace(hour=12, minute=30),
            'tag': 'coding',
            'label': 'Feature X'
        },
        {
            'start': datetime.now().replace(hour=14, minute=36),
            'end': datetime.now().replace(hour=17, minute=12),
            'tag': 'work',
            'label': 'Project Y'
        },
    ]
