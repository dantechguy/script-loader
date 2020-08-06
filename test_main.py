import unittest
import main

class TestCommonFunctions(unittest.TestCase):
    def test_exit_if_false(self):
        with self.assertRaises(SystemExit):
            main.func.exit_if_false(False)
        main.func.exit_if_false(True)
        
        
    def test_is_digit(self):
        values = [-7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5]
        for i in values+list(map(str, values)):
            with self.subTest(i=i):
                self.assertTrue(main.func.is_digit(i))
                
        values = ['hey' '100-12', '10-', '', None, 'None']
        for i in values:
            with self.subTest(i=i):
                self.assertFalse(main.func.is_digit(i))
        
            
    def test_between_function(self):
        between = main.func.between_function(-7, 5)
        
        nums = [-7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5]
        for i in nums+list(map(str, nums)):
            with self.subTest(i=i):
                self.assertTrue(between(i))
        
        nums = [-500, -100, -8, 6, 7, 100, 500, 'hi', '10o', '-one', None, 'None']
        for i in nums + list(map(str, nums)):
            with self.subTest(i=i):
                self.assertFalse(between(i))
                
                
    def test_get_list_index_string(self):
        test_dicts = [
            {
                'item_string': '{item} is #{index}',
                'item_list': [500, 550, 560, 570, 580],
                'expected': '''500 is #0
550 is #1
560 is #2
570 is #3
580 is #4'''
            },
            {
                'item_string': 'at position {index} lies {item}',
                'item_list': ['one', 2, 'THREE!', 4.00, '5', 666],
                'expected': '''at position 0 lies one
at position 1 lies 2
at position 2 lies THREE!
at position 3 lies 4.0
at position 4 lies 5
at position 5 lies 666'''
            },
        ]
        for item in test_dicts:
            with self.subTest(item=item):
                result = main.func.get_list_index_string(item['item_string'], item['item_list'])
                self.assertEqual(result, item['expected'])
        
                
    def test_check_missing_keys(self):
        main.func.check_missing_keys({1:2, 3:4, '5':'6', '1':'2'}, [1,3,'5','1'], '{key}')
        main.func.check_missing_keys({1:2}, [], '{key}')
        main.func.check_missing_keys({'ten',10}, ['ten'], '{key}')
        with self.assertRaises(KeyError):
            main.func.check_missing_keys({10:'ten'}, ['ten'], '{key}')
            
    def test_prefix_text(self):
        self.assertEqual(main.func.prefix_text('text', '--'), '--text')
        self.assertEqual(main.func.prefix_text('', '>> '), '')
        self.assertEqual(main.func.prefix_text('#comment\ntask', '#'), '##comment\n#task')
        self.assertEqual(main.func.prefix_text('\nnewline\n', '   '), '   \n   newline\n')
        self.assertEqual(main.func.prefix_text('\nnewline\n\n', '   '), '   \n   newline\n   \n')
        self.assertEqual(main.func.prefix_text('a', 'b'), 'ba')
        self.assertEqual(main.func.prefix_text('\n', '()'), '()\n')
        
    def test_ascii_only(self):
        for item in [
            ['mÿ string', 'm string'],
            ['þþþþþþ', ''],
            ['only ascii', 'only ascii']]:
            with self.subTest(item=item):
                result = main.func.ascii_only(item[0])
                self.assertEqual(result, item[1])













if __name__ == '__main__':
    unittest.main()
