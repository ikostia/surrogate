import sys
from functools import wraps
import importlib

__all__ = ('surrogate', )


class surrogate(object):
    """
        Add empty module stub that can be imported
        for every subpath in path.
        Those stubs can later be patched by mock's
        patch decorator.

        Example:

        @surrogate('sys.my.cool.module1')
        @surrogate('sys.my.cool.module2')
        @mock.patch('sys.my.cool.module1', mock1)
        @mock.patch('sys.my.cool.module2', mock2)
        def function():
            from sys.my import cool
            from sys.my.cool import module1
            from sys.my.cool import module2
    """

    def __init__(self, path):
        self.path = path
        self.elements = self.path.split('.')

    def __enter__(self):
        self.prepared = self.prepare()

    def __exit__(self, *args):
        if self.prepared:
            self.restore()

    def __call__(self, func):
        @wraps(func)
        def _wrapper(*args, **kwargs):
            prepared = self.prepare()
            result = func(*args, **kwargs)
            if prepared:
                self.restore()
            return result
        return _wrapper

    @property
    def nothing_to_stub(self):
        """Check if there are no modules to stub"""
        return len(self.elements) == 0

    def prepare(self):
        """Preparations before actual function call"""
        self._determine_existing_modules()
        if self.nothing_to_stub:
            return False
        self._create_module_stubs()
        self._save_base_module()
        self._add_module_stubs()
        return True

    def restore(self):
        """Post-actions to restore initial state of the system"""
        self._remove_module_stubs()
        self._restore_base_module()

    def _get_importing_path(self, elements):
        """Return importing path for a module that is last in elements list"""
        ip = '.'.join(elements)
        if self.known_path:
            ip = self.known_path + '.' + ip
        return ip

    def _create_module_stubs(self):
        """Create stubs for all not-existing modules"""
        # last module in our sequence
        # it should be loaded
        last_module = type(self.elements[-1], (object, ), {
            '__all__': [],
            '_importing_path': self._get_importing_path(self.elements)})
        modules = [last_module]

        # now we create a module stub for each
        # element in a path.
        # each module stub contains `__all__`
        # list and a member that
        # points to the next module stub in
        # sequence
        for element in reversed(self.elements[:-1]):
            next_module = modules[-1]
            module = type(element, (object, ), {
                next_module.__name__: next_module,
                '__all__': [next_module.__name__]})
            modules.append(module)
        self.modules = list(reversed(modules))
        self.modules[0].__path__ = []

    def _determine_existing_modules(self):
        """
            Find out which of the modules
            from specified path are already
            imported (e.g. present in sys.modules)
            those modules should not be replaced
            by stubs.
        """
        known = 0
        while known < len(self.elements) and\
                    '.'.join(self.elements[:known + 1]) in sys.modules:
            known += 1
        self.known_path = '.'.join(self.elements[:known])
        self.elements = self.elements[known:]

    def _save_base_module(self):
        """
            Remember state of the last of existing modules

            The last of the sequence of existing modules
            is the only one we will change. So we must
            remember it's state in order to restore it
            afterwards.
        """

        try:
            # save last of the existing modules
            self.base_module = sys.modules[self.known_path]
        except KeyError:
            self.base_module = None

        # save `__all__` attribute of the base_module
        self.base_all = []
        if hasattr(self.base_module, '__all__'):
            self.base_all = list(self.base_module.__all__)
        if self.base_module:
            # change base_module's `__all__` attribute
            # to include the first module of the sequence
            self.base_module.__all__ = self.base_all + [self.elements[0]]
            setattr(self.base_module, self.elements[0], self.modules[0])

    def _add_module_stubs(self):
        """Push created module stubs into sys.modules"""
        for i, module in enumerate(self.modules):
            module._importing_path =\
                self._get_importing_path(self.elements[:i + 1])
            sys.modules[module._importing_path] = module

    def _remove_module_stubs(self):
        """Remove fake modules from sys.modules"""
        for module in reversed(self.modules):
            if module._importing_path in sys.modules:
                del sys.modules[module._importing_path]

    def _restore_base_module(self):
        """Restore the state of the last existing module"""
        if self.base_module:
            self.base_module.__all__ = self.base_all
            if not self.base_all:
                del self.base_module.__all__
            if hasattr(self.base_module, self.elements[0]):
                delattr(self.base_module, self.elements[0])


def importorinject(modulename):
    """
    Returns a module if modulename exists or stubs it and returns the stub.

    This will import the modulename for the whole scope. There is no need to write @surrogate("modulename") before
    each test case. The intention is to provide something similar to  pytest.importorskip function:
    https://docs.pytest.org/en/6.2.x/reference.html#pytest-importorskip

    Usage:
        Instead of:

            import some_module

        that could potentially fail if there is no some_module, write this at test module level

            some_module = importorinject("some_module")

        Inside the test functions, some_module module/object will be available for usage, mocking, etc.

    Args:
        modulename: (str) The path/name of the module

    Returns:

    """
    surrogate_obj = surrogate(modulename)
    surrogate_obj.prepare()
    module = importlib.import_module(modulename)
    return module