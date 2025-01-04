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

def test_create_styled_text(visualizer):
    """Test that styled text has correct visible length"""
    # Test with different lengths
    for n in range(1, 10):
        styled = visualizer.create_styled_text("test", "white", "blue", n)
        visible_chars = len(styled.replace('\x1b', '').split('m')[-1])
        assert visible_chars == n, f"Styled text has {visible_chars} visible chars instead of {n}: {styled}"

def test_fixed_width_tag_labels(visualizer):
    """Test that tag labels maintain correct fixed width"""
    test_cases = [
        ('verylongtagname', 10),
        ('short', 10),
        ('tiny', 5)
    ]
    
    for tag, width in test_cases:
        label = visualizer.create_tag_label(tag, 'white', 'blue', width)
        visible_chars = len(label.replace('\x1b', '').split('m')[-1])
        assert visible_chars == width, f"Tag label has {visible_chars} visible chars instead of {width}: {label}"
        
        # Verify truncation/padding
        if len(tag) > width:
            assert label.replace('\x1b', '').split('m')[-1].strip() == tag[:width].strip()
        else:
            assert label.replace('\x1b', '').split('m')[-1].strip() == tag.strip()

def test_get_events_in_hour(visualizer, demo_events):
    """Test getting events in a specific hour"""
    # Test hour with multiple events
    test_hour = datetime.now().replace(hour=10, minute=0)
    events = visualizer.get_events_in_hour(demo_events, test_hour)
    
    # Should have 2 events: meeting ending at 10:30 and break starting at 10:30
    assert len(events) == 2
    assert events[0]['tag'] == 'meeting'
    # Meeting should cover 30 minutes (10:00-10:30)
    assert 29 <= events[0]['duration'] <= 30
    assert events[1]['tag'] == 'break'
    # Break should cover 30 minutes (10:30-11:00)
    assert 29 <= events[1]['duration'] <= 30
    
    # Test hour with single event
    test_hour = datetime.now().replace(hour=14, minute=0)
    events = visualizer.get_events_in_hour(demo_events, test_hour)
    assert len(events) == 1
    assert events[0]['tag'] == 'work'
    assert events[0]['duration'] == 60
    
    # Test hour with no events
    test_hour = datetime.now().replace(hour=3, minute=0)
    events = visualizer.get_events_in_hour(demo_events, test_hour)
    assert len(events) == 0

