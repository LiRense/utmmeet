class Solution:
    def romanToInt(self, s: str) -> int:
        d = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}
        c = 0
        prev_value = 0
        for char in s:
            current_value = d[char]
            if current_value > prev_value:
                dd = current_value - 2 * prev_value
                c += dd
            else:
                c += current_value
            prev_value = current_value


        return c


solution = Solution()
numer = input()
print(solution.romanToInt(numer))
