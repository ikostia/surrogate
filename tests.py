import unittest
from surrogate import surrogate, importorinject

def imports():
    import my
    import my.module
    import my.module.one
    import my.module.two
    from my import module
    from my.module import one, two
    return True

class TestSurrogateModuleStubs(unittest.TestCase):

    def test_surrogating(self):
        @surrogate('my')
        @surrogate('my.module.one')
        @surrogate('my.module.two')
        def stubbed():
            imports()

        try:
            stubbed()
        except Exception as e:
            raise Exception('Modules are not stubbed correctly: %r' % e)

        with self.assertRaises(ImportError) as e:
            imports()

    def test_context_manager(self):
        with surrogate('my'):
            with surrogate('my.module.one'):
                with surrogate('my.module.two'):
                    imports()


    def test_import_for_whole_module(self):
        some_module = importorinject("some_module")
        datetime = importorinject("datetime")

        assert some_module is not None
        assert datetime is not None
        result = datetime.date(2021, 4, 20)
        assert result is not None


if __name__ == '__main__':
    unittest.main()
