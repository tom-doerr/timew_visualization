#!/usr/bin/env python3
from datetime import datetime, timedelta
from termcolor import colored
from typing import List, Dict

class TimewarVisualizer:
    def __init__(self):
        self.tag_colors = {
            'work': 'blue',
            'meeting': 'green',
            'coding': 'yellow',
            'break': 'red',
        }
    
    def get_color_for_tag(self, tag: str) -> str:
        """Get color name for a tag, defaulting to white if not found"""
        return self.tag_colors.get(tag.lower(), 'white')
        
    def create_tag_label(self, tag: str, fg_color: str = 'white', bg_color: str = 'blue', width: int = 10) -> str:
        """Create a colored tag label with background, fixed width"""
        label = tag[:width] if len(tag) > width else tag.ljust(width)
        return colored(label, fg_color, f"on_{bg_color}")

    def get_events_in_hour(self, events: List[Dict], hour: datetime) -> List[Dict]:
        """Get all events happening in a specific hour"""
        hour_start = hour.replace(minute=0, second=0, microsecond=0)
        hour_end = hour_start + timedelta(hours=1)
        
        events_in_hour = []
        for event in events:
            if (event['start'] < hour_end) and (event['end'] > hour_start):
                overlap_start = max(event['start'], hour_start)
                overlap_end = min(event['end'], hour_end)
                duration = max(1, int((overlap_end - overlap_start).total_seconds() / 60))
                
                events_in_hour.append({
                    'tag': event['tag'],
                    'label': event.get('label', ''),
                    'start': overlap_start,
                    'end': overlap_end,
                    'duration': duration
                })
        
        return events_in_hour

    def get_hourly_summary(self, events: List[Dict]) -> Dict[str, Dict[str, int]]:
        """Get structured summary of time spent per tag in each hour.
        Includes untracked time and ensures each hour sums to 60 minutes."""
        if not events:
            return {}

        start_time = min(e['start'] for e in events).replace(minute=0, second=0, microsecond=0)
        end_time = max(e['end'] for e in events).replace(minute=0, second=0, microsecond=0)
        
        hourly_summary = {
            (start_time + timedelta(hours=i)).strftime("%H:%M"): {}
            for i in range(int((end_time - start_time).total_seconds() // 3600) + 1)
        }

        for event in events:
            current_time = event['start'].replace(minute=0, second=0, microsecond=0)
            while current_time < event['end']:
                hour_key = current_time.strftime("%H:%M")
                end_of_hour = current_time + timedelta(hours=1)
                duration = min(event['end'], end_of_hour) - max(event['start'], current_time)
                duration_min = max(0, int(round(duration.total_seconds() / 60)))
                
                if duration_min > 0:
                    if event['tag'] not in hourly_summary[hour_key]:
                        hourly_summary[hour_key][event['tag']] = 0
                    hourly_summary[hour_key][event['tag']] += duration_min
                
                current_time = end_of_hour

        # Add untracked time
        for hour_key, tags in hourly_summary.items():
            total_tracked = sum(tags.values())
            untracked = 60 - total_tracked
            if untracked > 0:
                hourly_summary[hour_key]['untracked'] = untracked
        
        return hourly_summary

    def create_timeline(self, events: List[Dict]) -> None:
        """Create and display a timeline visualization"""
        if not events:
            print(colored("No events to display", "red"))
            return
        
        # Show hourly summary first
        print("\nHourly Summary:")
        summary = self.get_hourly_summary(events)
        for hour, tags in summary.items():
            print(f"{hour}:")
            for tag, minutes in tags.items():
                print(f"  {tag}: {minutes} minutes")
        print()
            
        start_time = min(e['start'] for e in events).replace(minute=0, second=0, microsecond=0)
        end_time = max(e['end'] for e in events).replace(minute=0, second=0, microsecond=0)
        
        current_hour = start_time
        while current_hour <= end_time:
            hour_label = current_hour.strftime("%H:%M")
            timeline = []
            
            for minute in range(60):
                time_point = current_hour + timedelta(minutes=minute)
                active_event = next(
                    (e for e in events if e['start'] <= time_point < e['end']),
                    None
                )
                
                if active_event:
                    color = self.get_color_for_tag(active_event['tag'])
                    char = self.create_tag_label(
                        active_event['tag'] if time_point == active_event['start'] else ' ',
                        fg_color='white',
                        bg_color=color
                    )
                else:
                    char = colored("░", attrs=['dark'])
                
                timeline.append(char)
            
            print(f"{colored(hour_label, attrs=['bold'])} {''.join(timeline)}")
            current_hour += timedelta(hours=1)
