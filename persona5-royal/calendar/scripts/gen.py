import re
import datetime
import pathlib

from html.parser import HTMLParser
from jinja2 import Template

DATE_PATTERN = re.compile(r'^(\d+)月(.+)日.*周(.*)')

class PersonaDay(object):
    def __init__(self, date):
        self.date = date
        self.lines = []

    def __repr__(self):
        return '{}\n{}'.format(self.date, self.lines)

    def relative_path(self):
        return '{}/{}.html'.format(self.date.month, self.date.day)


class CalendarParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.entries = []
        self.p_level = 0

    def handle_starttag(self, tag, attrs):
        if tag == 'p':
            self.p_level += 1


    def handle_endtag(self, tag):
        if tag == 'p':
            self.p_level -= 1


    def handle_data(self, data):
        if self.p_level <= 0:
            return

        # Extract the date if this line is a date
        c = DATE_PATTERN.match(data)
        if c is not None:
            month = int(c.group(1))
            new_date = datetime.date(2016 if month >= 4 else 2017, month, int(c.group(2)))
            # Check for date continuity
            if len(self.entries) > 0:
                expected_date = self.entries[-1].date + datetime.timedelta(days=1)
                while expected_date != new_date:
                    print('Warning: {} is missing.'.format(expected_date))
                    expected_date += datetime.timedelta(days=1)
            self.entries.append(PersonaDay(new_date))
        elif len(self.entries) > 0:
            self.entries[-1].lines.append(data)

parser = CalendarParser()

with open('data/first.html', 'r') as f:
    parser.feed(f.read())

with open('data/second.html', 'r') as f:
    parser.feed(f.read())

output_dir = '/home/breakds/Downloads/persona5'

template = Template('''
<html>
  <head>
    <title>Persona 5 Royal Calendar by 黑桐谷歌</title>
    <link rel="stylesheet" type="text/css" href="https://cdnjs.cloudflare.com/ajax/libs/semantic-ui/2.4.1/semantic.min.css">
    <script
      src="https://code.jquery.com/jquery-3.1.1.min.js"
      integrity="sha256-hVVnYaiADRTO2PzUGmuLJr8BLUSjGIZsDYGmIJLv2b8="
      crossorigin="anonymous"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/semantic-ui/2.4.1/semantic.min.js" ></script>
    <script>
      $(document).ready(function() {
          $('.ui.dropdown').dropdown();
          $('#partition').click(function() {
              $('#partition').addClass('loading');
          });
      });
    </script>
  </head>
  <body>
  <div class="ui container">
    <div class="ui piled segment">
      <h2 class="ui header">{{ title }}</h2>
      {% for line in lines %}
      <p>{{ line }}</p>
      {% endfor %}
      <div class="inline">
        <a class="ui green tiny button {{ prev_visible }}" 
           href="{{ prev_link }}">{{ prev }}</a>
        <a class="ui orange tiny button {{ next_visible}}"
           href="{{ next_link }}">{{ next }}</a>
      </div>
    </div>
  </div>
  </body>
</html>
''')
    
for i, entry in enumerate(parser.entries):
    date_text = entry.date.strftime('%m月%d日 %a')
    html_path = pathlib.Path(output_dir, entry.relative_path())
    html_path.parent.mkdir(parents=True, exist_ok=True)

    prev_visible = 'disabled'
    next_visible = 'disabled'
    prev = 'Prev'
    next = 'next'
    prev_link = ''
    next_link = ''

    if i > 0:
        prev_visible = ''
        prev = parser.entries[i - 1].date.strftime('%m月%d日')
        prev_link = '/{}'.format(parser.entries[i - 1].relative_path())

    if i + 1 < len(parser.entries):
        next_visible = ''
        next = parser.entries[i + 1].date.strftime('%m月%d日')
        next_link = '/{}'.format(parser.entries[i + 1].relative_path())
    
    with open(html_path, 'w') as out:
        out.write(template.render(title=date_text, lines=entry.lines,
                                  prev_visible=prev_visible,
                                  next_visible=next_visible,
                                  prev=prev, next=next,
                                  prev_link=prev_link, next_link=next_link))
