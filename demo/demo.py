class DemoCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    # assignments will be joined to one line
    variable_1 = 'test 1'
    variable_2 = 'test 2'
    variable_3 = 'test 3'

  def _method(self):
    # assignments will be unjoined to several lines
    variable_1, variable_2, variable_3 = 'test 1', 'test 2', 'test 3'
