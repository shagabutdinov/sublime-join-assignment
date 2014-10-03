# Sublime JoinAssignment plugin

Handy plugin that automate joining/unjoining multiple assignments. I rejoiced
when I did this plugin because joining/unojoining assigmnment is stupid
operation that requires a lot of keyhits when doing it manually.

### Demo

![Demo](https://raw.github.com/shagabutdinov/sublime-join-assignment/master/demo/demo.gif "Demo")


### Installation

This plugin is part of [sublime-enhanced](http://github.com/shagabutdinov/sublime-enhanced)
plugin set. You can install sublime-enhanced and this plugin will be installed
automatically.

If you would like to install this package separately check "Installing packages
separately" section of [sublime-enhanced](http://github.com/shagabutdinov/sublime-enhanced)
package.

### Usage

1. Join assignment

  ```
  # before
  var1 = call1() # cursor anywhere at this line
  var2 = call2()

  # after
  var1, var2 = call1(), call2()
  ```

2. Unjoin assignment

  ```
  # before
  var1, var2 = call1(), call2() # cursor at this line

  # after
  var1 = call1()
  var2 = call2()

  ```

### Commands

| Description       | Keyboard shortcut | Command palette        |
|-------------------|-------------------|------------------------|
| Join assignment   | ctrl+w            | JoinAssignment: join   |
| Unjoin assignment | ctrl+shift+w      | JoinAssignment: unjoin |