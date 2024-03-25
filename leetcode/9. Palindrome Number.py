
class Solution:
    def isPalindrome(self, x: int) -> bool:
        x = str(x)
        return  x[::-1] == x[::1]



solution = Solution()
print(solution.isPalindrome(1234567890))