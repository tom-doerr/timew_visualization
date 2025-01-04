#!/usr/bin/env python3
from datetime import datetime, timedelta
from rich.console import Console
from rich.text import Text
from rich.style import Style
from typing import List, Dict, Optional
import sys

class TimewarVisualizer:
    def __init__(self):
        self.console = Console()
        self.tag_styles = {
            'work': Style(color='blue', bold=True),
            'meeting': Style(color='green', bold=True),
            'coding': Style(color='yellow', bold=True),
            'break': Style(color='red', bold=True),
        }
    
    def get_style_for_tag(self, tag: str) -> Style:
        """Get style for a tag, defaulting to white if not found"""
        return self.tag_styles.get(tag.lower(), Style(color='white'))
    
    def create_timeline(self, events: List[Dict]) -> None:
        """Create and display a timeline visualization"""
        if not events:
            self.console.print("No events to display", style="red")
            return
            
        # Group events by hour
        current_hour = events[0]['start'].replace(minute=0, second=0, microsecond=0)
        end_time = events[-1]['end']
        
        while current_hour <= end_time:
            # Create the hour label
            hour_label = current_hour.strftime("%H:%M")
            
            # Create the timeline bar
            timeline = Text()
            for minute in range(60):
                time_point = current_hour + timedelta(minutes=minute)
                # Find active event at this minute
                active_event = next(
                    (e for e in events if e['start'] <= time_point < e['end']),
                    None
                )
                
                if active_event:
                    char = "█"
                    style = self.get_style_for_tag(active_event['tag'])
                    # Add text label at the start of the event
                    if time_point == active_event['start']:
                        # Use a different character for text segments with padding
                        char = f"▓{active_event['label']}▓"
                        style = style + Style(bgcolor="black")
                else:
                    char = "░"
                    style = Style(dim=True)
                
                timeline.append(char, style=style)
            
            # Print the hour line
            self.console.print(f"{hour_label} {timeline}")
            current_hour += timedelta(hours=1)

if __name__ == "__main__":
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
    ]
    
    visualizer = TimewarVisualizer()
    visualizer.create_timeline(demo_events)
