"""Core rendering logic"""
import copy
import os
from typing import Iterator, List, Tuple, Dict
from collections import defaultdict, namedtuple

import pyte
from lxml import etree

from termcap.parser.asciicast import AsciiCastV2Event, AsciiCastV2Header
from termcap.renderer import svg, theme

# Default size for a character cell rendered as SVG.
CELL_WIDTH = 8
CELL_HEIGHT = 17
FRAME_CELL_SPACING = 1

TimedFrame = namedtuple('TimedFrame', ['time', 'duration', 'buffer'])

def render_animation(
    records: Iterator[AsciiCastV2Event],
    header: AsciiCastV2Header,
    output_path: str,
    template_name: str,
    min_frame_dur: int = 1,
    max_frame_dur: int = None,
    loop_delay: int = 1000
):
    """Render asciicast records to SVG animation"""
    
    # Load template
    template_content = theme.load_template(template_name)
    if not template_content:
        raise ValueError(f"Template '{template_name}' not found")
        
    # Generate frames
    geometry, frames_generator = timed_frames(
        records, header, min_frame_dur, max_frame_dur, loop_delay
    )
    
    # Prepare SVG
    columns, rows = geometry
    root = svg.resize_template(template_content, columns, rows, CELL_WIDTH, CELL_HEIGHT)
    
    # Clear existing screen content
    screen_tag = root.find(f'.//{{{svg.SVG_NS}}}svg[@id="screen"]')
    for child in screen_tag.getchildren():
        screen_tag.remove(child)
        
    # Add background rect
    bg_rect = etree.Element('rect', {
        'class': 'background',
        'height': '100%',
        'width': '100%',
        'x': '0',
        'y': '0'
    })
    screen_tag.append(bg_rect)
    
    # Render frames
    screen_view = etree.Element('g', attrib={'id': 'screen_view'})
    definitions = {}
    timings = {}
    animation_duration = 0
    
    frames = list(frames_generator) # Consume generator
    screen_height = rows * CELL_HEIGHT
    
    for frame_count, frame in enumerate(frames):
        rows_per_frame = rows + FRAME_CELL_SPACING
        offset = frame_count * (rows_per_frame + rows_per_frame % 2) * CELL_HEIGHT
        
        frame_group = etree.Element('g')
        group_definitions = {}
        
        for row_number, line_data in frame.buffer.items():
            if line_data:
                current_definitions = {**definitions, **group_definitions}
                tags, new_defs = svg.render_line(
                    offset, row_number, line_data, CELL_WIDTH, CELL_HEIGHT, current_definitions
                )
                for tag in tags:
                    frame_group.append(tag)
                group_definitions.update(new_defs)
        
        screen_view.append(frame_group)
        definitions.update(group_definitions)
        
        animation_duration = frame.time + frame.duration
        timings[frame.time] = -offset
        
    # Add definitions
    defs_tag = etree.SubElement(screen_tag, 'defs')
    for definition in definitions.values():
        defs_tag.append(definition)
        
    screen_tag.append(screen_view)
    
    # Add CSS animation
    svg.embed_css(root, timings, animation_duration)
    
    # Write output
    with open(output_path, 'wb') as f:
        f.write(etree.tostring(root))

def render_still_frames(
    records: Iterator[AsciiCastV2Event],
    header: AsciiCastV2Header,
    output_dir: str,
    template_name: str,
    min_frame_dur: int = 1,
    max_frame_dur: int = None,
    loop_delay: int = 1000
):
    """Render asciicast records to still SVG frames"""
    template_content = theme.load_template(template_name)
    if not template_content:
        raise ValueError(f"Template '{template_name}' not found")
        
    geometry, frames_generator = timed_frames(
        records, header, min_frame_dur, max_frame_dur, loop_delay
    )
    columns, rows = geometry
    root = svg.resize_template(template_content, columns, rows, CELL_WIDTH, CELL_HEIGHT)
    
    os.makedirs(output_dir, exist_ok=True)
    
    for i, frame in enumerate(frames_generator):
        frame_root = copy.deepcopy(root)
        screen_tag = frame_root.find(f'.//{{{svg.SVG_NS}}}svg[@id="screen"]')
        for child in screen_tag.getchildren():
            screen_tag.remove(child)
            
        bg_rect = etree.Element('rect', {
            'class': 'background',
            'height': '100%',
            'width': '100%',
            'x': '0',
            'y': '0'
        })
        screen_tag.append(bg_rect)
        
        definitions = {}
        frame_group = etree.Element('g')
        
        for row_number, line_data in frame.buffer.items():
            if line_data:
                tags, new_defs = svg.render_line(
                    0, row_number, line_data, CELL_WIDTH, CELL_HEIGHT, definitions
                )
                for tag in tags:
                    frame_group.append(tag)
                definitions.update(new_defs)
                
        defs_tag = etree.SubElement(screen_tag, 'defs')
        for definition in definitions.values():
            defs_tag.append(definition)
            
        screen_tag.append(frame_group)
        svg.embed_css(frame_root, None, None)
        
        with open(os.path.join(output_dir, f'frame_{i:05d}.svg'), 'wb') as f:
            f.write(etree.tostring(frame_root))

def timed_frames(records, header, min_frame_dur, max_frame_dur, last_frame_dur):
    """Generate TimedFrame objects from records"""
    
    if not max_frame_dur and header.idle_time_limit:
        max_frame_dur = int(header.idle_time_limit * 1000)
        
    def generator():
        screen = pyte.Screen(header.width, header.height)
        stream = pyte.Stream(screen)
        
        # Group records by time
        grouped_records = _group_by_time(records, min_frame_dur, max_frame_dur, last_frame_dur)
        
        for record in grouped_records:
            stream.feed(record.event_data)
            yield TimedFrame(
                int(1000 * record.time),
                int(1000 * record.duration),
                _screen_buffer(screen)
            )
            
    return (header.width, header.height), generator()


def _group_by_time(records, min_rec_duration, max_rec_duration, last_rec_duration):
    """Group events by time"""
    current_string = ''
    current_time = 0
    dropped_time = 0
    
    if max_rec_duration:
        max_rec_duration /= 1000.0
        
    for event in records:
        if event.event_type != 'o':
            continue
            
        time_between_events = event.time - (current_time + dropped_time)
        if time_between_events * 1000 >= min_rec_duration:
            if max_rec_duration and max_rec_duration < time_between_events:
                dropped_time += time_between_events - max_rec_duration
                time_between_events = max_rec_duration
                
            yield AsciiCastV2Event(
                time=current_time,
                event_type='o',
                event_data=current_string,
                duration=time_between_events
            )
            
            current_string = ''
            current_time += time_between_events
            
        current_string += event.event_data
        
    yield AsciiCastV2Event(
        time=current_time,
        event_type='o',
        event_data=current_string,
        duration=last_rec_duration / 1000.0
    )


def _screen_buffer(screen):
    buffer = defaultdict(dict)
    for row in range(screen.lines):
        buffer[row] = {
            column: _char_to_cell(screen.buffer[row][column])
            for column in screen.buffer[row]
        }
    
    # Cursor
    if not screen.cursor.hidden:
        row, column = screen.cursor.y, screen.cursor.x
        if 0 <= row < screen.lines and 0 <= column < screen.columns:
            try:
                data = screen.buffer[row][column].data
            except KeyError:
                data = ' '
            
            cursor_char = pyte.screens.Char(
                data=data,
                fg=screen.cursor.attrs.fg,
                bg=screen.cursor.attrs.bg,
                reverse=True
            )
            buffer[row][column] = _char_to_cell(cursor_char)
            
    return buffer

def _char_to_cell(char):
    # Mapping logic for colors
    fg = char.fg
    bg = char.bg
    
    # Simplify color mapping for now
    if fg == 'default': fg = 'foreground'
    elif fg in svg.CharacterCell._fields: pass 
    
    if bg == 'default': bg = 'background'
    
    # Handle reverse
    if char.reverse:
        fg, bg = bg, fg
        
    return svg.CharacterCell(
        text=char.data,
        color=str(fg),
        background_color=str(bg),
        bold=char.bold,
        italics=char.italics,
        underscore=char.underscore,
        strikethrough=char.strikethrough
    )
