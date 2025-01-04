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
                    char = colored("█", color, f"on_{color}")
                    # Add text label at the start of the event
                    if time_point == active_event['start']:
                        # Generate random colors
                        colors = ['red', 'green', 'blue', 'yellow', 'magenta', 'cyan']
                        bg_color = random.choice(colors)
                        fg_color = random.choice([c for c in colors if c != bg_color])
                        char = colored(f"▓{active_event['label']}▓", fg_color, f"on_{bg_color}")
                else:
                    char = colored("░", attrs=['dark'])
                
                timeline.append(char)
            
            # Print the hour line
            print(f"{colored(hour_label, attrs=['bold'])} {''.join(timeline)}")
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
