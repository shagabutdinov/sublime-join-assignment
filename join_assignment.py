import sublime
import sublime_plugin
import re

from Statement import statement
from Expression import expression

def _get_parts(view, point):
  container = statement.get_root_statement(view, point)
  if container == None:
    return None

  assignment_match = expression.find_match(view, container[0], r'\s+=\s+',
    {'range': container})

  if assignment_match == None:
    return None

  part_1 = [container[0], container[0] + assignment_match.start(0)]
  part_2 = [container[0] + assignment_match.end(0), container[1]]

  return part_1, part_2

class JoinAssignment(sublime_plugin.TextCommand):
  def run(self, edit):
    for selection in self.view.sel():
      self._join(edit, selection)

  def _join(self, edit, selection):
    if not selection.empty():
      return

    first = _get_parts(self.view, selection.b)
    if first == None:
      return

    region = sublime.Region(first[1][1], self.view.size())
    match = re.search(r'\S', self.view.substr(region))
    if match == None:
      return

    second = _get_parts(self.view, region.a + match.start(0))
    if second == None:
      return

    second_part_1, second_part_2 = second

    value_1 = ', ' + self.view.substr(sublime.Region(*second_part_1))
    value_2 = ', ' + self.view.substr(sublime.Region(*second_part_2))

    if re.search(r';$', value_2):
      value_2 = value_2[:-1]

    erase_region = self.view.full_line(sublime.Region(second_part_1[0],
      second_part_2[1]))
    self.view.erase(edit, erase_region)

    self._insert(edit, first[0], first[1], value_1, value_2)

  def _insert(self, edit, region_1, region_2, value_1, value_2):
    region_1_value = self.view.substr(sublime.Region(*region_1))
    region_2_value = self.view.substr(sublime.Region(*region_2))

    if region_2_value.endswith(';'):
      region_2_value = region_2_value[:-1]
      region_2[1] -= 1

    is_php = 'php' in self.view.scope_name(region_1[1])

    # php hack 1
    if is_php:
      if region_1_value.startswith('list('):
        region_1_value = region_1_value[:-1]
        region_1[1] -= 1
        region_2_value = region_2_value[:-1]
        region_2[1] -= 1

    self.view.insert(edit, region_2[1], value_2)
    self.view.insert(edit, region_1[1], value_1)

    # php hack 2
    if not is_php:
      return

    info = _get_parts(self.view, region_1[1])
    if info == None:
      return

    part_1, part_2 = info

    part_1_region = sublime.Region(*part_1)
    part_1_value = self.view.substr(part_1_region)

    part_2_region = sublime.Region(part_2[0], part_2[1])
    part_2_value = self.view.substr(part_2_region)

    if part_2_value.endswith(';'):
      part_2_value = part_2_value[:-1]
      part_2_region.b -= 1

    append_array = (not part_2_value.startswith('array(') and
      not part_2_value.startswith('['))

    if append_array:
      self.view.replace(edit, part_2_region, '[' + part_2_value + ']')

    if not part_1_value.startswith('list('):
      self.view.replace(edit, part_1_region, 'list(' + part_1_value + ')')

class UnjoinAssignment(sublime_plugin.TextCommand):
  def run(self, edit):
    for selection in self.view.sel():
      self._unjoin(edit, selection)

  def _unjoin(self, edit, selection):
    is_php = 'php' in self.view.scope_name(selection.b)
    tokens = self._get_tokens(selection, is_php)
    if tokens == None:
      return

    point, semicolon, tokens_1, tokens_2, _, _ = tokens
    if len(tokens_1) <= 1 or len(tokens_2) <= 1:
      return

    token_1 = self.view.substr(sublime.Region(*tokens_1[-1]))
    token_2 = self.view.substr(sublime.Region(*tokens_2[-1]))

    new_statement = "\n"

    line_region = self.view.line(tokens_1[0][0])
    spaces = re.search(r'^\s+', self.view.substr(line_region))
    if spaces:
      new_statement += spaces.group(0)

    new_statement += token_1 + ' = ' + token_2
    if semicolon:
      new_statement += ';'

    self.view.insert(edit, point, new_statement)

    self.view.erase(edit, sublime.Region(tokens_2[-2][1], tokens_2[-1][1]))
    self.view.erase(edit, sublime.Region(tokens_1[-2][1], tokens_1[-1][1]))

    if not is_php:
      return

    self._finalize(edit, tokens_1[0][0], is_php)

  def _finalize(self, edit, point, is_php):
    tokens = self._get_tokens(sublime.Region(point, point), is_php)
    if tokens == None:
      return

    _, semicolon, tokens_1, tokens_2, part_1, part_2 = tokens
    if len(tokens_1) != 1 or len(tokens_2) != 1:
      return

    part_2_value = self.view.substr(sublime.Region(*part_2))
    remove = None
    if part_2_value.startswith('array('):
      remove = 6
    elif part_2_value.startswith('['):
      remove = 1
    else:
      return

    if semicolon:
      shift = 1
    else:
      shift = 0

    erase_region = sublime.Region(part_2[1] - shift - 1, part_2[1] - shift)
    self.view.erase(edit, erase_region)
    self.view.erase(edit, sublime.Region(part_2[0], part_2[0] + remove))

    part_1_value = self.view.substr(sublime.Region(*part_1))
    if not part_1_value.startswith('list('):
      return

    self.view.erase(edit, sublime.Region(part_1[1] - 1, part_1[1]))
    self.view.erase(edit, sublime.Region(part_1[0], part_1[0] + 5))

  def _get_tokens(self, selection, is_php):
    if not selection.empty():
      return None

    parts = _get_parts(self.view, selection.b)
    if parts == None:
      return None

    part_1, part_2 = parts[0].copy(), parts[1].copy()
    point = part_2[1]

    part_1_value = self.view.substr(sublime.Region(*part_1))
    part_2_value = self.view.substr(sublime.Region(*part_2))

    semicolon = False;
    if part_2_value.endswith(';'):
      part_2_value = part_2_value[:-1]
      part_2[1] -= 1
      semicolon = True

    # php hacks
    if is_php:
      if part_1_value.startswith('list('):
        part_1[0] += 5
        part_1[1] -= 1

      if part_2_value.startswith('array('):
        part_2[0] += 5
        part_2[1] -= 1
      elif part_2_value.startswith('['):
        part_2[0] += 1
        part_2[1] -= 1

    tokens_1 = statement.get_tokens(self.view, selection.b, part_1)
    tokens_2 = statement.get_tokens(self.view, selection.b, part_2)

    return point, semicolon, tokens_1, tokens_2, parts[0], parts[1]