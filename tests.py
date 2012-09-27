import unittest
from surrogate import surrogate


class TestSurrogateModuleStubs(unittest.TestCase):

    def test_surrogating(self):

        def imports():
            import my
            import my.module
            import my.module.one
            import my.module.two
            from my import module
            from my.module import one, two
            return True

        @surrogate('my')
        @surrogate('my.module.one')
        @surrogate('my.module.two')
        def stubbed():
            imports()

        try:
            stubbed()
        except Exception, e:
            raise Exception('Modules are not stubbed correctly: %r' % e)

        with self.assertRaises(ImportError) as e:
            imports()

if __name__ == '__main__':
    unittest.main()
