About
=====

``surrogate`` is a micro-lib helping people to create stubs
for non-existing modules in ``sys.modules`` so that later
those modules can be imported. ``surrogate`` does not touch
modules that exist in ``sys.modules`` even if you ask it to.

At the moment ``surrogate`` offers only decorator interface
but it is planned to add context-manager interface as well.

Intention
=========

Once author needed to write tests for a function that
works only in production (but not in developement env).
Those function imported modules that did not exist in
development environment. Thus, in order to test those
function, mocking of the aforementioned modules was
necessary. Unfortunately, author did not manage to
mock those modules with `patch` decorator from
``mock`` library. It was necessary to create module stubs
first and then to mock them. This micro-lib does exactly
what author needed (except of the mistakes, of course).

Usage
=====

Please, use ``surrogate`` as a function decorator::

    from surrogate import surrogate

    @surrogate('sys.my.cool.module.stub1')
    @surrogate('sys.my.cool.module.stub2')
    def test_something():
        from sys.my.cool.module import stub1
        from sys.my.cool.module import stub2
        import sys.my.cool as cool
        import sys # this is a normal sys module
        do_something()


Accourding to intention, you can use `surrogate`
with `mock.patch` decorators::

    from surrogate import surrogate
    from mock import patch

    @surrogate('this.module.doesnt.exist')
    @patch('this.module.doesnt.exits', whatever)
    def test_something():
        from this.module.doesnt import exist
        do_something()


LICENSE
=======

This code can be used, distributed and modified 
in any ways one wants. If one gets any use of it
author is already rewarded.
On the other hand, do not expect any guaranteed
support from author. Use it as is.
