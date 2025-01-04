import pytest
from datetime import datetime, timedelta
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

def test_create_tag_label(visualizer):
    """Test tag label creation with fixed width"""
    label = visualizer.create_tag_label('test', width=10)
    assert len(label.replace('\x1b', '').split('m')[-1]) == 10
    
    long_label = visualizer.create_tag_label('verylongtagname', width=10)
    assert len(long_label.replace('\x1b', '').split('m')[-1]) == 10

def test_get_events_in_hour(visualizer, demo_events):
    """Test getting events in a specific hour"""
    test_hour = datetime.now().replace(hour=10, minute=0)
    events = visualizer.get_events_in_hour(demo_events, test_hour)
    
    assert len(events) == 2
    assert events[0]['tag'] == 'meeting'
    assert 29 <= events[0]['duration'] <= 30
    assert events[1]['tag'] == 'break'
    assert 29 <= events[1]['duration'] <= 30

def test_get_hourly_summary(visualizer, demo_events):
    """Test getting structured hourly summary"""
    summary = visualizer.get_hourly_summary(demo_events)
    
    assert '10:00' in summary
    assert summary['10:00']['meeting'] == 30
    assert summary['10:00']['break'] == 30
    assert sum(summary['10:00'].values()) == 60
    
    assert '14:00' in summary
    assert summary['14:00']['work'] == 24
    assert summary['14:00']['untracked'] == 36
    
    # Test all hours sum to 60 minutes
    for hour, tags in summary.items():
        assert sum(tags.values()) == 60

