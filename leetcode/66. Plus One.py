from typing import List


class Solution:
    def plusOne(self, digits: List[int]) -> List[int]:
        digits = map(str,digits)
        number = ''.join(digits)
        number = list(str(int(number)+1))
        return map(int,number)



sol = Solution()
print(sol.plusOne([1,2,3]))