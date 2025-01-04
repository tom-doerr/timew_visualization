import pytest
from datetime import datetime
from timewar_visualizer import TimewarVisualizer

@pytest.fixture
def visualizer():
    return TimewarVisualizer()

@pytest.fixture
def demo_events():
    return [
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

def test_create_wrapped_timeline(visualizer, demo_events):
    wrapped_timeline = visualizer.create_wrapped_timeline(demo_events)
    lines = wrapped_timeline.split('\n')
    
    # Check all lines except last one have exactly 60 visible chars
    for line in lines[:-1]:
        # Remove ANSI escape sequences before counting
        visible_chars = len(line.replace('\x1b', '').split('m')[-1])
        assert visible_chars == 60, f"Line has {visible_chars} visible chars instead of 60: {line}"
    
    # Last line can be shorter than 60 chars
    if lines[-1]:
        visible_chars = len(lines[-1].replace('\x1b', '').split('m')[-1])
        assert visible_chars <= 60, f"Last line has {visible_chars} visible chars (should be <=60): {lines[-1]}"
