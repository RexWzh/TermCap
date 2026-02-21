"""SVG generation logic"""
import io
import os
from lxml import etree
from wcwidth import wcswidth
from itertools import groupby
from typing import NamedTuple, List, Dict, Any, Tuple

# XML namespaces
SVG_NS = 'http://www.w3.org/2000/svg'
TERMCAP_NS = 'https://github.com/rexwzh/termcap'
XLINK_NS = 'http://www.w3.org/1999/xlink'

class TemplateError(Exception):
    pass

class CharacterCell(NamedTuple):
    text: str
    color: str
    background_color: str
    bold: bool
    italics: bool
    underscore: bool
    strikethrough: bool

class ConsecutiveWithSameAttributes:
    def __init__(self, attributes):
        self.group_index = None
        self.last_index = None
        self.attributes = attributes
        self.last_key_attributes = None

    def __call__(self, arg):
        index, obj = arg
        key_attributes = {name: getattr(obj, name) for name in self.attributes}
        if self.last_index != index - 1 or self.last_key_attributes != key_attributes:
            self.group_index = index
        self.last_index = index
        self.last_key_attributes = key_attributes
        return self.group_index, key_attributes

def make_rect_tag(column, length, height, cell_width, cell_height, background_color):
    attributes = {
        'x': str(column * cell_width),
        'y': str(height),
        'width': str(length * cell_width),
        'height': str(cell_height)
    }

    if background_color.startswith('#'):
        attributes['fill'] = background_color
    else:
        attributes['class'] = background_color
    return etree.Element('rect', attributes)

def make_text_tag(column, attributes, text, cell_width):
    text_tag_attributes = {
        'x': str(column * cell_width),
        'textLength': str(wcswidth(text) * cell_width),
    }
    if attributes['bold']:
        text_tag_attributes['font-weight'] = 'bold'

    if attributes['italics']:
        text_tag_attributes['font-style'] = 'italic'

    decoration = ''
    if attributes['underscore']:
        decoration = 'underline'
    if attributes['strikethrough']:
        decoration += ' line-through'
    if decoration:
        text_tag_attributes['text-decoration'] = decoration

    if attributes['color'].startswith('#'):
        text_tag_attributes['fill'] = attributes['color']
    else:
        text_tag_attributes['class'] = attributes['color']

    text_tag = etree.Element('text', text_tag_attributes)
    text_tag.text = text
    return text_tag

def render_line(y_offset, row_number, line_data, cell_width, cell_height, definitions):
    """Render a single line of terminal output"""
    tags = []
    
    # Background
    non_default_bg_cells = [(column, cell) for (column, cell)
                            in sorted(line_data.items())
                            if cell.background_color != 'background']

    key = ConsecutiveWithSameAttributes(['background_color'])
    for (column, attributes), group in groupby(non_default_bg_cells, key):
        length = wcswidth(''.join(t[1].text for t in group))
        tags.append(make_rect_tag(
            column,
            length,
            y_offset + row_number * cell_height,
            cell_width,
            cell_height,
            attributes['background_color']
        ))

    # Text
    text_group_tag = etree.Element('g')
    line_items = sorted(line_data.items())
    key = ConsecutiveWithSameAttributes(['color', 'bold', 'italics', 'underscore', 'strikethrough'])
    
    for (column, attributes), group in groupby(line_items, key):
        text = ''.join(c.text for _, c in group)
        text_group_tag.append(make_text_tag(column, attributes, text, cell_width))

    # Reuse definition if possible
    text_group_tag_str = etree.tostring(text_group_tag)
    new_definitions = {}
    
    if text_group_tag_str in definitions:
        group_id = definitions[text_group_tag_str].attrib['id']
    else:
        group_id = 'g{}'.format(len(definitions) + 1)
        text_group_tag.attrib['id'] = group_id
        new_definitions = {text_group_tag_str: text_group_tag}

    use_attributes = {
        f'{{{XLINK_NS}}}href': f'#{group_id}',
        'y': str(y_offset + row_number * cell_height),
    }
    tags.append(etree.Element('use', use_attributes))

    return tags, new_definitions

def resize_template(template_content: bytes, columns: int, rows: int, cell_width: int, cell_height: int) -> etree.Element:
    """Resize template based on the number of rows and columns of the terminal"""
    try:
        tree = etree.parse(io.BytesIO(template_content))
        root = tree.getroot()
    except etree.Error as exc:
        raise TemplateError('Invalid template') from exc

    settings = root.find(f'.//{{{SVG_NS}}}defs/{{{TERMCAP_NS}}}template_settings')
    if settings is None:
        raise TemplateError('Missing "template_settings"')

    svg_geometry = settings.find(f'{{{TERMCAP_NS}}}screen_geometry')
    if svg_geometry is None:
        raise TemplateError('Missing "screen_geometry"')

    try:
        template_columns = int(svg_geometry.attrib['columns'])
        template_rows = int(svg_geometry.attrib['rows'])
    except (KeyError, ValueError):
        raise TemplateError('Invalid geometry attributes')

    svg_geometry.attrib['columns'] = str(columns)
    svg_geometry.attrib['rows'] = str(rows)

    _scale_element(root, template_columns, template_rows, columns, rows, cell_width, cell_height)

    screen = root.find(f'.//{{{SVG_NS}}}svg[@id="screen"]')
    if screen is None:
        raise TemplateError('svg element with id "screen" not found')
    _scale_element(screen, template_columns, template_rows, columns, rows, cell_width, cell_height)

    return root

def _scale_element(element, template_columns, template_rows, columns, rows, cell_width, cell_height):
    if 'viewBox' in element.attrib:
        viewbox = [int(n) for n in element.attrib['viewBox'].replace(',', ' ').split()]
        viewbox[2] += cell_width * (columns - template_columns)
        viewbox[3] += cell_height * (rows - template_rows)
        element.attrib['viewBox'] = ' '.join(map(str, viewbox))

    for attr, delta in [('width', cell_width * (columns - template_columns)),
                        ('height', cell_height * (rows - template_rows))]:
        if attr in element.attrib:
            try:
                val = int(element.attrib[attr])
                element.attrib[attr] = str(val + delta)
            except ValueError:
                pass

def embed_css(root, timings, animation_duration):
    try:
        style = root.find(f'.//{{{SVG_NS}}}defs/{{{SVG_NS}}}style[@id="generated-style"]')
    except etree.Error as exc:
        raise TemplateError('Invalid template') from exc

    if style is None:
        raise TemplateError('Missing <style id="generated-style" ...> element')

    css_body = """#screen {
                font-family: 'DejaVu Sans Mono', monospace;
                font-style: normal;
                font-size: 14px;
            }

        text {
            dominant-baseline: text-before-edge;
            white-space: pre;
        }
    """

    if animation_duration is None or timings is None:
        style.text = etree.CDATA(css_body)
    else:
        if animation_duration == 0:
            raise ValueError('Animation duration must be greater than 0')

        transforms = []
        last_offset = None
        transform_format = "{time:.3f}%{{transform:translateY({offset}px)}}"
        for time, offset in sorted(timings.items()):
            transforms.append(
                transform_format.format(
                    time=100.0 * time/animation_duration,
                    offset=offset
                )
            )
            last_offset = offset

        if last_offset is not None:
            transforms.append(
                transform_format.format(time=100, offset=last_offset)
            )

        css_animation = """
            :root {{
                --animation-duration: {duration}ms;
            }}

            @keyframes roll {{
                {transforms}
            }}

            #screen_view {{
                animation-duration: {duration}ms;
                animation-iteration-count:infinite;
                animation-name:roll;
                animation-timing-function: steps(1,end);
                animation-fill-mode: forwards;
            }}
        """.format(
            duration=animation_duration,
            transforms=os.linesep.join(transforms)
        )

        style.text = etree.CDATA(css_body + css_animation)
    return root
