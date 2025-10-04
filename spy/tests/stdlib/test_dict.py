import pytest
from spy.tests.support import CompilerTest


class TestDict(CompilerTest):

    def test_set_get_simple(self):
        src = """
        from dict import dict

        def test() -> int:
            d = dict[i32, i32]()
            d[1] = 10
            d[2] = 20
            return d[1] + d[2]
        """
        mod = self.compile(src)
        assert mod.test() == 30

    def test_overwrite_value(self):
        src = """
        from dict import dict

        def test() -> int:
            d = dict[i32, i32]()
            d[1] = 1
            d[1] = 3
            return d[1]
        """
        mod = self.compile(src)
        assert mod.test() == 3

    def test_len_and_no_growth_on_update(self):
        src = """
        from dict import dict

        def test() -> int:
            d = dict[i32, i32]()
            d[1] = 1
            d[2] = 2
            d[3] = 3
            # updating an existing key should not change the length
            d[2] = 22
            return len(d)
        """
        mod = self.compile(src)
        assert mod.test() == 3

    def test_missing_key_raises(self):
        src = """
        from dict import dict

        def test() -> int:
            d = dict[i32, i32]()
            return d[99]
        """
        mod = self.compile(src)
        with pytest.raises(Exception, match="KeyError"):
            mod.test()

    def test_many_inserts_and_lookup(self):
        src = """
        from dict import dict

        def test(n: i32) -> int:
            d = dict[i32, i32]()
            i = 1
            while i <= n:
                d[i] = i
                i += 1
            return d[n]
        """
        mod = self.compile(src)
        assert mod.test(10) == 10
        # MIN_LOG_SIZE = 6 => 64 entries
        # MAX_FILL_RATIO = 2 / 3 => 43 entries to trigger resize
        assert mod.test(43) == 43
        # and 86 entries to trigger two resizes
        assert mod.test(86) == 86

    def test_len_after_many_inserts(self):
        src = """
        from dict import dict

        def test(n: i32) -> int:
            d = dict[i32, i32]()
            i = 0
            while i < n:
                d[i] = i
                i += 1
            return len(d)
        """
        mod = self.compile(src)
        assert mod.test(10) == 10

    def test_delete(self):
        src = """
        from dict import dict
        
        def test() -> int:
            d = dict[i32, i32]()
            d[1] = 1
            # del d[1]
            d.__delitem__(1)
            return len(d)
        """
        mod = self.compile(src)
        assert mod.test() == 0

    def test_delete_twice_raises(self):
        src = """
        from dict import dict
        
        def test() -> int:
            d = dict[i32, i32]()
            d[1] = 1
            # del d[1]
            d.__delitem__(1)
            d.__delitem__(1)
            return len(d)
        """
        mod = self.compile(src)
        with pytest.raises(Exception, match="KeyError"):
            mod.test()

    def test_fastiter(self):
        src = """
        from dict import dict

        def test() -> int:
            d = dict[i32, i32]()
            d[10] = -1
            d[20] = -1
            d[30] = -1
            it = d.__fastiter__()
            total = 0
            while it.__continue_iteration__():
                total = total + it.__item__()
                it = it.__next__()
            return total
        """
        mod = self.compile(src)
        assert mod.test() == 60

    def test_for_loop(self):
        src = """
        from dict import dict

        def test() -> int:
            d = dict[i32, i32]()
            d[1] = -1
            d[2] = -1
            d[3] = -1
            d[4] = -1
            total = 0
            for x in d:
                total = total + x
            return total
        """
        mod = self.compile(src)
        assert mod.test() == 10

    def test_contains(self):
        src = """
        from dict import dict
        
        def test() -> bool:
            d = dict[i32, i32]()
            d[1] = 1
            return d.__contains__(1)
        """
        mod = self.compile(src)
        assert mod.test()

    def test_equal(self):
        src = """
        from dict import dict
        
        def test_eq() -> bool:
            d1 = dict[i32, i32]()
            d1[1] = -1
            d1[2] = -1
            d1[3] = -1
            d2 = dict[i32, i32]()
            d2[1] = -1
            d2[2] = -1
            d2[3] = -1
            return d1 == d2
        
        def test_neq_value() -> bool:
            d1 = dict[i32, i32]()
            d1[1] = -1
            d1[2] = -1
            d1[3] = -1
            d2 = dict[i32, i32]()
            d2[1] = -1
            d2[2] = -1
            d2[3] = 0
            return d1 == d2
        
        def test_neq_missing_key() -> bool:
            d1 = dict[i32, i32]()
            d1[1] = -1
            d1[2] = -1
            d1[3] = -1
            d2 = dict[i32, i32]()
            d2[1] = -1
            d2[2] = -1
            return d1 == d2
        
        def test_neq_key() -> bool:
            d1 = dict[i32, i32]()
            d1[1] = -1
            d1[2] = -1
            d1[3] = -1
            d2 = dict[i32, i32]()
            d2[1] = -1
            d2[2] = -1
            d1[33] = -1
            return d1 == d2
        """
        mod = self.compile(src)
        assert mod.test_eq()
        assert not mod.test_neq_value()
        assert not mod.test_neq_missing_key()
        assert not mod.test_neq_key()
